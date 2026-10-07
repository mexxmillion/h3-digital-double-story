"""Export the local dance experiment as a public, self-contained media bundle."""
import argparse
import hashlib
import json
import re
import subprocess
import zipfile
from pathlib import Path


SITE = Path(__file__).resolve().parents[1] / 'site/dance'


def ffmpeg(*args):
    subprocess.run(['ffmpeg', '-hide_banner', '-loglevel', 'error', '-y', *map(str, args)], check=True)


def probe(path):
    return json.loads(subprocess.check_output(['ffprobe', '-v', 'error', '-count_frames', '-select_streams', 'v:0', '-show_entries', 'stream=width,height,r_frame_rate,nb_read_frames', '-of', 'json', str(path)]))['streams'][0]


def audio_hash(path, packets=False):
    return subprocess.check_output(['ffmpeg', '-v', 'error', '-i', str(path), '-map', '0:a:0', *(['-c', 'copy'] if packets else []), '-f', 'hash', '-hash', 'sha256', '-']).decode().strip()


def main(root, reuse_media=False):
    root = root.resolve()
    job = root / 'output/H3_Dance_New_Hard_Cuts'
    media = SITE / 'media'
    media.mkdir(parents=True, exist_ok=True)
    manifest = []
    exports = [
        ('final.mp4', job / 'Dance_full_take1_motion_repair_original_audio.mp4', None, 22),
        ('source-final.mp4', job / 'Source_vs_Result_full_take1_motion_repair.mp4', '960:-2', 23),
        ('source-restitch.mp4', job / 'source_cut_audit/Source_restitch_original_audio.mp4', '480:-2', 23),
        ('focus-7-13.mp4', job / 'take1_drift_repair/Source_vs_New_7to13.mp4', '960:-2', 22),
        ('seam-one.mp4', job / 'take1_drift_repair/Transition_322_Source_vs_Result.mp4', '960:-2', 22),
        ('seam-two.mp4', job / 'take1_drift_repair/Transition_579_Source_vs_Result.mp4', '960:-2', 22),
        ('inverted-depth.mp4', root / 'output/H3_Dance_Full_Sequence/cut3_guide_comparison/Source_Inverted_Depth.mp4', '960:-2', 23),
        ('protected-overlap.mp4', root / 'output/H3_Dance_Overlap_Test/Source_Independent_Protected.mp4', '960:-2', 23),
    ]
    for name, source, scale, crf in exports:
        target = media / name
        filters = ['-vf', f'scale={scale}'] if scale else []
        if not reuse_media or not target.exists():
            ffmpeg('-i', source, '-map', '0:v:0', '-map', '0:a:0?', *filters, '-map_metadata', -1, '-map_chapters', -1, '-c:v', 'libx264', '-preset', 'fast', '-crf', crf, '-pix_fmt', 'yuv420p', '-c:a', 'copy', '-movflags', '+faststart', target)
        assert probe(source)['nb_read_frames'] == probe(target)['nb_read_frames']
        ffmpeg('-i', target, '-ss', 1, '-frames:v', 1, '-map_metadata', -1, '-q:v', 3, media / (target.stem + '.jpg'))
        manifest.append({'asset': 'media/' + name, 'provenance': source.name, 'video': probe(target), 'bytes': target.stat().st_size, 'sha256': hashlib.sha256(target.read_bytes()).hexdigest()})
    comparisons = [
        ('take1-source-old-new.mp4', [root / 'output/H3_Dance_Full_Sequence/source_24fps.mp4', job / 'take1/generated/selected_cut.mp4', job / 'take1_drift_repair/result.mp4'], 168, 312),
        ('middle-source-old-new.mp4', [job / 'source_cut_audit/cut2_source_lossless.mp4', job / 'take2/generated/selected_cut.mp4', job / 'take2_pose_repair/result.mp4'], 0, 257),
    ]
    for name, sources, first, last in comparisons:
        inputs = []
        filters = []
        for i, source in enumerate(sources):
            inputs += ['-i', source]
            filters.append(f'[{i}:v]trim=start_frame={first}:end_frame={last},setpts=PTS-STARTPTS,scale=320:560[v{i}]')
        filters.append('[v0][v1][v2]hstack=inputs=3[out]')
        target = media / name
        if not reuse_media or not target.exists():
            ffmpeg(*inputs, '-filter_complex', ';'.join(filters), '-map', '[out]', '-an', '-map_metadata', -1, '-c:v', 'libx264', '-preset', 'fast', '-crf', 20, '-pix_fmt', 'yuv420p', '-movflags', '+faststart', target)
        assert int(probe(target)['nb_read_frames']) == last - first
        ffmpeg('-i', target, '-ss', 2, '-frames:v', 1, '-map_metadata', -1, '-q:v', 3, media / (target.stem + '.jpg'))
        manifest.append({'asset': 'media/' + name, 'provenance': [p.name for p in sources], 'source_frames': [first, last], 'silent': True, 'video': probe(target), 'bytes': target.stat().st_size})
    bundle = SITE / 'downloads'
    assets = bundle / 'input/h3_mobile/dance_case_study/take1'
    assets.mkdir(parents=True, exist_ok=True)
    original_inputs = root / 'input/h3_mobile/H3_Dance_New_Hard_Cuts/take1_drift_repair'
    for name in ['reference_sheet.png', 'anchor_0.png', 'anchor_144.png', 'anchor_192.png', 'anchor_264.png', 'anchor_321.png']:
        ffmpeg('-i', original_inputs / name, '-frames:v', 1, '-map_metadata', -1, assets / name)
    ffmpeg('-i', original_inputs / 'guide_padded.mp4', '-map', '0:v:0', '-map', '0:a:0?', '-map_metadata', -1, '-map_chapters', -1, '-c', 'copy', '-movflags', '+faststart', assets / 'guide_padded.mp4')
    old_input = 'h3_mobile/H3_Dance_New_Hard_Cuts/take1_drift_repair'
    new_input = 'h3_mobile/dance_case_study/take1'
    old_output = 'H3_Dance_New_Hard_Cuts/take1_drift_repair/generated/pose_control_v1'
    for target, source in [
        ('take1-api.json', job / 'take1_drift_repair/graphs/pose_control_v1_api.json'),
        ('take1-workflow.json', root / 'user/default/workflows/H3 Shot Replace/H3_Dance_New_Hard_Cuts/take1_drift_repair/pose_control_v1.json'),
    ]:
        text = source.read_text(encoding='utf-8').replace(old_input, new_input).replace(old_output, 'dance_case_study/take1')
        assert not re.search(r'(?<![A-Za-z])[A-Za-z]:[\\/]|(?:^|[\\/])Users[\\/]', text)
        (bundle / target).write_text(text, encoding='utf-8')
    (bundle / 'README.txt').write_text('Take-one pose-anchor example. Copy the input/ directory into your ComfyUI root, then import take1-workflow.json. API graph: take1-api.json. Existing model files and node contracts are required; no model weights or credentials are included. Guide length328; deliver322 frames at24fps. Arbitrary frame Add Guide for MiniMax H3 nodes:41,43,45,47,49 at0,144,192,264,321. This is a sanitized version of the inspected run; local paths/output prefix were changed for sharing. Tested on Windows/CUDA RTX3090; other installs may have different node schemas. See the case-study settings and node table before queueing.\n', encoding='utf-8')
    with zipfile.ZipFile(SITE / 'take1-workflow-and-inputs.zip', 'w', zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(bundle.rglob('*')):
            if path.is_file():
                archive.write(path, path.relative_to(bundle).as_posix())
    ffmpeg('-i', job / 'take1_drift_repair/source_11s.png', '-frames:v', 1, '-map_metadata', -1, media / 'source-11s.webp')
    source_audio = json.loads((root / 'output/H3_Dance_White_10s_AB/manifest.json').read_text())['source']
    audio_checks = {}
    for packets in [True, False]:
        hashes = [audio_hash(path, packets) for path in [source_audio, media / 'final.mp4', media / 'source-final.mp4']]
        assert len(set(hashes)) == 1, ('Public full-video audio mismatch', hashes)
        audio_checks['compressed_aac' if packets else 'decoded_pcm'] = hashes[0]
    source_check = json.loads((job / 'source_cut_audit/source_restitch_verification.json').read_text())
    checks = {'normalized_source_restitch': source_check, 'public_full_video_audio_hashes': audio_checks, 'public_full_frame_count': 1023, 'fps': 24, 'cuts': [322, 579, 927], 'timebase': 'zero-based24fps; exclusive end boundaries', 'web_export': 'Video reencoded for web; full final/comparison AAC streams copied unchanged. Other previews can use source excerpts. Visual comparisons are sampled human review, not a quality score.', 'take1_generation_seconds': 3015.9, 'middle_generation_seconds': 2047.7, 'limitations': ['Small identity/expression/hand/partner deviations remain', 'No isolated ablation of prompt correction versus pose guides', 'Long-context adaptation rejected for source choreography drift']}
    (SITE / 'verification.json').write_text(json.dumps(checks, indent=2), encoding='utf-8')
    (SITE / 'media-manifest.json').write_text(json.dumps(manifest, indent=2), encoding='utf-8')
    for path in SITE.rglob('*'):
        if path.is_file() and path.stat().st_size > 25 * 1024 * 1024:
            raise RuntimeError(f'Public asset exceeds25MiB: {path.name}')
    print(f'Exported {len(manifest)} video assets; audio and frame counts verified.', flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('comfy_root', type=Path)
    parser.add_argument('--reuse-media', action='store_true', help='Reuse existing video exports after a packaging-only repair; frame counts are still checked.')
    args = parser.parse_args()
    main(args.comfy_root, args.reuse_media)
