from pathlib import Path
import json,csv
import numpy as np
import matplotlib;matplotlib.use('Agg')
import matplotlib.pyplot as plt
P=Path(__file__).resolve().parent;S=json.loads((P/'analysis_summary.json').read_text());raw=[json.loads(f.read_text()) for f in sorted((P/'states').glob('*/result.json'))];rows=[r for s in raw for r in s['results']];res=list(csv.DictReader((P/'residuals.csv').open()));colors={'true':'#126987','random':'#b96924'}
plt.rcParams.update({'font.size':10,'axes.spines.top':False,'axes.spines.right':False})
fig,axs=plt.subplots(1,2,figsize=(12,4.5),layout='constrained')
for ax,g in zip(axs,['true','random']):
 rr=[r for r in S['correlations'] if r['regime']==g];x=[r['radius'] for r in rr];y=[r['rho_common_endpoint'] for r in rr];ax.plot(x,y,'o-',color=colors[g],label='Radio común: máximo angular');ax.fill_between(x,[r['rho_boot_low'] for r in rr],[r['rho_boot_high'] for r in rr],color=colors[g],alpha=.15,label='Intervalo descriptivo por splits');ax.axhline(rr[0]['rho_nominal_disk'],color='gray',ls='--',label='Nominal: máximo dentro del disco');ax.axhline(rr[0]['rho_nominal_endpoint'],color='black',ls=':',label='Nominal: máximo angular del borde');ax.axvline(S['primary_radius'],color='gray',alpha=.3);ax.set(title=g,xlabel='Radio geodésico común',ylabel='Spearman C_A–condición');ax.set_ylim(-1,1.05);ax.legend(fontsize=8,loc='lower right')
fig.suptitle('E15-T1-B — sensibilidad al radio; intervalos sin interpretación confirmatoria');fig.savefig(P/'correlation_sensitivity.png',dpi=180);plt.close(fig)
fig,axs=plt.subplots(1,2,figsize=(12,4.6),layout='constrained')
for g in ['true','random']:
 rr=[r for r in rows if r['radius_index']==2 and r['regime']==g and r['C_A']is not None];axs[0].scatter([r['C_A'] for r in rr],[max(r['kappa_max']-1,1e-12) for r in rr],label=g,color=colors[g],alpha=.8)
axs[0].set_xscale('log');axs[0].set_yscale('log');axs[0].set(title='Radio principal: C_A admisible únicamente',xlabel='C_A sobre dominio nominal propio',ylabel='κ máximo − 1');axs[0].legend()
rr=sorted([r for r in rows if r['radius_index']==2 and r['regime']=='true'],key=lambda r:-r['kappa_max']);axs[1].plot(range(1,41),[r['kappa_max'] for r in rr],'.-',color=colors['true'])
for i,r in enumerate(rr,1):
 if r['T1A_classification']=='GEOMETRIC_NONINJECTIVITY':
  axs[1].scatter(i,r['kappa_max'],marker='*',color='#a12846',s=140,zorder=4);axs[1].annotate(r['state'].replace('split0_',''),(i,r['kappa_max']),xytext=(5,8),textcoords='offset points',fontsize=9)
axs[1].axvspan(.5,4.5,color='gold',alpha=.12,label='Cola predefinida: top 4/40');axs[1].set(xlabel='Rango descendente dentro de true',ylabel='κ máximo',title='Los dos positivos incluidos, sin C_A artificial');axs[1].legend(fontsize=8)
fig.suptitle(f'E15-T1-B — radio común principal r={S["primary_radius"]:.8f}');fig.savefig(P/'common_radius_and_positive_cases.png',dpi=180);plt.close(fig)
rr=[r for r in res if r['radius_index']=='2' and r['regime']=='true'];fig,axs=plt.subplots(2,3,figsize=(13,7),layout='constrained')
for ax,m,label in zip(axs.flat,['C_A','nominal_radius','lambda_1pct','R_eff','angular_K_abs_cv','angular_K_peak_to_rms'],['C_A','Radio nominal propio','Lambda 1%','R_eff','CV angular de |K|','Máximo |K| / RMS angular']):
 x=[float(r[m]) for r in rr];y=[float(r['residual_log10']) for r in rr];ax.scatter(x,y,c=[int(r['split']) for r in rr],cmap='tab10',vmin=0,vmax=9,alpha=.8);ax.axhline(0,color='gray',lw=.8);ax.axhline(np.log10(2),color='gray',ls='--',lw=.8);ax.axhline(-np.log10(2),color='gray',ls='--',lw=.8);ax.set(xlabel=label,ylabel='Residuo log10(κ−1)');
 if m in ['C_A','R_eff']:ax.set_xscale('log')
fig.suptitle('Residuos true — tendencia isotónica dejando un split fuera; líneas = factor 2');fig.savefig(P/'residual_diagnostics.png',dpi=180);plt.close(fig)
fig,axs=plt.subplots(1,2,figsize=(12,4.5),layout='constrained')
rr=[r for r in rows if r['radius_index']==2 and r['regime']=='true' and r['C_A']is not None]
axs[0].scatter([r['nominal_radius'] for r in rr],[r['C_A'] for r in rr],color=colors['true']);axs[0].set_yscale('log');axs[0].set(xlabel='Radio nominal para A=0.02',ylabel='C_A',title='Asociación radio–curvatura')
for key,label,marker in [('kappa_nominal_endpoint','Radio nominal propio','o'),('kappa_max','Radio común','x')]:axs[1].scatter([r['nominal_radius'] for r in rr],[max(r[key]-1,1e-12) for r in rr],label=label,marker=marker)
axs[1].set_yscale('log');axs[1].set(xlabel='Radio nominal propio',ylabel='κ máximo − 1',title='Cambio descriptivo de escala');axs[1].legend()
fig.suptitle('Área objetivo fija y radio: no identifica mediación causal');fig.savefig(P/'fixed_area_effect.png',dpi=180);plt.close(fig)
print('4 diagnostic figures saved')
