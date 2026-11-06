"""릴리즈 xdelta 를 해시 검사 후 적용.
사용: python tools/apply_release.py --xdelta xdelta3.exe --source "Assault Suit Leynos 2 (Japan) (Track 01).bin" --patch Leynos2_SS_KO_v1.0.xdelta --output "Assault Suit Leynos 2 (Korean) (Track 01).bin"
트랙 2~14(음악)는 바뀌지 않으므로 원본 음악 트랙을 그대로 가리키는 CUE를 만든다.
"""
import argparse, hashlib, json, os, subprocess, sys

MAN = json.load(open(os.path.join(os.path.dirname(__file__), '..', 'release_manifest.json'), encoding='utf-8'))

def sha256(p):
    h = hashlib.sha256()
    with open(p, 'rb') as f:
        for b in iter(lambda: f.read(1 << 22), b''): h.update(b)
    return h.hexdigest()

def check(p, size, digest, what):
    if os.path.getsize(p) != size: sys.exit('%s 크기 불일치: %d (기대 %d)' % (what, os.path.getsize(p), size))
    print(what, '해시 확인 중...', flush=True)
    if sha256(p) != digest: sys.exit('%s SHA-256 불일치' % what)

a = argparse.ArgumentParser()
a.add_argument('--xdelta', default='xdelta3')
a.add_argument('--source', required=True, help='원본 트랙 1 BIN')
a.add_argument('--patch', required=True)
a.add_argument('--output', required=True)
o = a.parse_args()
if os.path.exists(o.output): sys.exit('출력 파일이 이미 있습니다: ' + o.output)
check(o.source, MAN['source_bin_size'], MAN['source_bin_sha256'], '원본 트랙 1 BIN')
check(o.patch, MAN['asset_size'], MAN['asset_sha256'], 'xdelta')
subprocess.run([o.xdelta, '-d', '-s', o.source, o.patch, o.output], check=True)
check(o.output, MAN['output_bin_size'], MAN['output_bin_sha256'], '결과 트랙 1 BIN')
cue = os.path.splitext(o.output)[0].replace(' (Track 01)', '') + '.cue'
src_cue = os.path.splitext(o.source)[0].replace(' (Track 01)', '') + '.cue'
if os.path.exists(cue):
    print('CUE가 이미 있어 만들지 않았습니다:', cue)
elif not os.path.exists(src_cue):
    print('원본 CUE를 찾지 못해 CUE를 만들지 않았습니다:', src_cue)
else:
    srcdir = os.path.dirname(os.path.abspath(o.source)); outdir = os.path.dirname(os.path.abspath(o.output))
    out = []; first = True
    for l in open(src_cue, encoding='utf-8', errors='replace').read().splitlines():
        if l.startswith('FILE "'):
            name = l.split('"')[1]
            if first: name = os.path.basename(o.output); first = False
            else: name = os.path.relpath(os.path.join(srcdir, name), outdir)
            l = 'FILE "%s" BINARY' % name
        out.append(l)
    open(cue, 'w', encoding='utf-8').write('\n'.join(out) + '\n')
    print('CUE 생성:', cue)
print('완료:', o.output)
