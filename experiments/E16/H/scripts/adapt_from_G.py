#!/usr/bin/env python3
"""Adaptación explícita G→H: entrada/procedencia y sin emparejamiento con F."""
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]

def adapt(source):
    replacements=[
      ('E16-G: resolución diagnóstica, sin alterar los criterios ni salidas de F.',
       'E16-H: transferencia prospectiva del método G a configuraciones nuevas.'),
      ("D=ROOT.parent/'D';F=ROOT.parent/'F'", "D=ROOT.parent/'D';G=ROOT.parent/'G'"),
      ("assert sha(D/'config.json')==CFG['source_config_sha256']", "assert sha(ROOT/'data.json')==CFG['source_config_sha256']"),
      ("assert sha(F/'results/run_v1/lengths.csv')==CFG['F_lengths_sha256']", "assert sha(G/'scripts/run.py')==CFG['source_G_sha256']"),
      ("source=json.loads((D/'config.json').read_text())\n    oldrows=list(csv.DictReader((F/'results/run_v1/lengths.csv').open()))\n    old={f\"{r['state']}/{r['panel']}/{r['path']}/{r['composition']}\":r for r in oldrows}",
       "source=json.loads((ROOT/'data.json').read_text())\n    assert source['rho']==method_rho()"),
      ('rows=[];checks=[];lower={};pairedvalues={};comparisons=[]','rows=[];checks=[];lower={};pairedvalues={}'),
      ("                            frow=old[key]\n                            comparisons.append({'state':state,'panel':panel,'path':path,'composition':kind,'F_status':frow['status'],'G_status':status,\n                                'F_L16':frow['L16'],'G_length':row['length'],\n                                'normalized_difference':fmt(err(length,mp.mpf(frow['L16']))) if length is not None else ''})\n",''),
      ("    transitions={}\n    for r in comparisons:\n        name=r['F_status']+'->'+r['G_status'];transitions[name]=transitions.get(name,0)+1\n",''),
      ("'paired':len(paired),'transitions_from_F':transitions,'descriptive':desc", "'paired':len(paired),'descriptive':desc"),
      ("writecsv(out/'paired_ratios.csv',paired);writecsv(out/'comparison_F.csv',comparisons);dump(out/'summary.json',summary)",
       "writecsv(out/'paired_ratios.csv',paired);dump(out/'summary.json',summary)"),
      ("dump(out/'provenance.json',{'D_config_sha256':sha(D/'config.json'),'D_method_sha256':sha(D/'scripts/run.py'),\n        'F_lengths_sha256':sha(F/'results/run_v1/lengths.csv'),'G_config_sha256':sha(ROOT/'config.json'),\n        'G_script_sha256':sha(Path(__file__)),'design_commit':'7049807','python':sys.version.split()[0],'mpmath':mp.__version__,\n        'analysis':'diagnóstico de datos F; no confirmación independiente'})",
       "dump(out/'provenance.json',{'D_method_sha256':sha(D/'scripts/run.py'),'G_method_sha256':sha(G/'scripts/run.py'),\n        'H_data_sha256':sha(ROOT/'data.json'),'H_config_sha256':sha(ROOT/'config.json'),\n        'H_script_sha256':sha(Path(__file__)),'design_commit':'3c96c95','python':sys.version.split()[0],'mpmath':mp.__version__,\n        'analysis':'transferencia prospectiva instrumental; no validación predictiva'})"),
      ("'checks':cc,'transitions':transitions,'seconds':elapsed", "'checks':cc,'seconds':elapsed"),
      ("def main(out):", "def method_rho():\n    return json.loads((D/'config.json').read_text())['rho']\n\ndef main(out):"),
    ]
    for before,after in replacements:
        assert source.count(before)==1, before
        source=source.replace(before,after,1)
    return source

if __name__=='__main__':
    source=(ROOT.parent/'G/scripts/run.py').read_text()
    (ROOT/'scripts/run.py').write_text(adapt(source))
