from pathlib import Path
import hashlib,json,sys
root=Path(__file__).resolve().parent
manifest=json.loads((root/'PACKAGE_SHA256.json').read_text())
errors=[]
for name,expected in manifest.items():
 p=root/name
 if not p.is_file() or hashlib.sha256(p.read_bytes()).hexdigest()!=expected:errors.append(name)
if errors:
 print('FAIL',errors);sys.exit(1)
print('PASS:',len(manifest),'archivos; SHA-256 coincidentes')
