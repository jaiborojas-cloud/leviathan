"""Hessianos y Rayleigh: diagnóstico local; no certificación de mínimo."""
import numpy as np
import mpmath as mp
from autograd import grad,hessian

def rel(a,b):return abs(a-b)/max(1,abs(a),abs(b))
def analyze(name,z,objL,objE,a,b,ux,uy,k,cfg,check):
    x=k.pack(z,'free');length=float(objL.value(x));gl=np.asarray(grad(objL.value)(x),float)
    hl=np.asarray(hessian(objL.value)(x),float);he=np.asarray(hessian(objE.value)(x),float)
    ha=np.asarray(hessian(lambda xx:objL.value(xx)**2/2)(x),float)
    expected=length*hl+np.outer(gl,gl)
    check(name+'/arc_hessian',float(np.max(abs(ha-expected)))/max(1,float(np.max(abs(ha))),float(np.max(abs(expected)))),cfg['hessian_identity_tolerance'])
    bounds=np.array([bb for j in range(len(z)-2) for bb in [cfg['t_bounds'],cfg['s_bounds']]])
    inactive=np.minimum(abs(x-bounds[:,0]),abs(x-bounds[:,1]))>float(cfg['boundary_tolerance'])
    spectra=[];directions=[];m=len(z)-1
    for target,h in [('length',hl),('energy',he),('arc',ha)]:
        reduced=h[np.ix_(inactive,inactive)];vals=np.linalg.eigvalsh((reduced+reduced.T)/2)
        if not len(vals):raise ValueError('empty inactive Hessian block')
        floor=cfg['spectral_relative_floor']*max(1,float(np.max(abs(vals))));positive=vals[vals>floor];negative=vals[vals<-floor];zero=vals[abs(vals)<=floor]
        spectra.append({'point':name,'objective':target,'dimension':len(x),'inactive_dimension':int(np.sum(inactive)),
            'min_eigenvalue':repr(float(vals[0])),'max_eigenvalue':repr(float(vals[-1])),'threshold':repr(floor),
            'negative':len(negative),'near_zero':len(zero),'positive':len(positive),
            'positive_spectrum_ratio':repr(float(positive[-1]/positive[0])) if len(positive) else '',
            'classification':'INDEFINITE' if len(negative) else ('NEAR_SINGULAR' if len(zero) else 'POSITIVE_AT_THRESHOLD')})
    tangent=z[2:]-z[:-2];norm=np.linalg.norm(tangent,axis=1)
    tangent=np.divide(tangent,norm[:,None],out=np.zeros_like(tangent),where=norm[:,None]>0)
    normal=np.column_stack([-tangent[:,1],tangent[:,0]])
    with mp.workdps(80):
        pts=k.mp_points(a,b,z);v=b-a;nmp=mp.matrix([-v[1],v[0]])
        for direction,field in [('tangent',tangent),('normal',normal)]:
            vector=field.reshape(-1);vector=np.where(inactive,vector,0.);size=np.linalg.norm(vector)
            if size==0:
                check(name+'/'+direction+'/nonzero',1,0,'conditioning')
                directions.append({'point':name,'direction':direction,'objective':'unknown','ad_rayleigh':'','mp_step_1':'','mp_step_2':'','ad_error':'','step_error':'','status':'INCONCLUSIVE'});continue
            vector=vector/size;vf=vector.reshape((-1,2));dp=[mp.mpf(float(q[0]))*v+mp.mpf(float(q[1]))*nmp for q in vf]
            for target,h,reference in [('length',hl,k.reference),('energy',he,k.reference_energy)]:
                value=reference(pts,objL.kind,ux,uy);second=[]
                for step in cfg['hessian_fd_steps']:
                    step=mp.mpf(step);plus=[pts[0]]+[p+step*d for p,d in zip(pts[1:-1],dp)]+[pts[-1]];minus=[pts[0]]+[p-step*d for p,d in zip(pts[1:-1],dp)]+[pts[-1]]
                    second.append((reference(plus,objL.kind,ux,uy)-2*value+reference(minus,objL.kind,ux,uy))/(step*step))
                ray=float(vector@h@vector);error=rel(mp.mpf(ray),second[1]);step_error=rel(*second)
                check(name+'/'+direction+'/'+target+'/ad',error,cfg['hessian_direction_tolerance'],'conditioning')
                check(name+'/'+direction+'/'+target+'/steps',step_error,cfg['hessian_fd_agreement_tolerance'],'conditioning')
                directions.append({'point':name,'direction':direction,'objective':target,'ad_rayleigh':repr(ray),'mp_step_1':mp.nstr(second[0],40),'mp_step_2':mp.nstr(second[1],40),'ad_error':mp.nstr(error,40),'step_error':mp.nstr(step_error,40),'status':'PASS' if error<=mp.mpf(cfg['hessian_direction_tolerance']) and step_error<=mp.mpf(cfg['hessian_fd_agreement_tolerance']) else 'INCONCLUSIVE'})
        if objL.kind=='sum':
            jmat=mp.matrix([[v[0],nmp[0]],[v[1],nmp[1]]]);frame=jmat.T*(ux*ux.T)*jmat
            f=np.array(frame.tolist(),float);t=2*np.eye(m-1)-np.eye(m-1,k=1)-np.eye(m-1,k=-1);analytic=m*np.kron(t,f)
            check(name+'/sum_energy_hessian',float(np.max(abs(he-analytic)))/max(1,float(np.max(abs(analytic)))),cfg['hessian_identity_tolerance'])
            # Exact metric control on a straight curve with the same t, without modifying z.
            straight=np.column_stack([z[:,0],np.zeros(len(z))]);p=k.mp_points(a,b,straight);j=len(p)//2
            delta=(mp.mpf(float(straight[j+1,0]))-mp.mpf(float(straight[j-1,0])))/20
            if delta<=0:raise ValueError('non-monotone sum control')
            plus=p.copy();minus=p.copy();plus[j]=p[j]+delta*v;minus[j]=p[j]-delta*v
            l0=k.reference(p,'sum',ux,uy);lp=k.reference(plus,'sum',ux,uy);lm=k.reference(minus,'sum',ux,uy)
            check(name+'/sum_tangential_length',max(rel(l0,lp),rel(l0,lm)),cfg['precision_tolerance'])
            e0=k.reference_energy(p,'sum',ux,uy);ep=k.reference_energy(plus,'sum',ux,uy);em=k.reference_energy(minus,'sum',ux,uy)
            curvature=(ep-2*e0+em)/(delta*delta);check(name+'/sum_tangential_energy',rel(curvature,2*m*frame[0,0]),cfg['precision_tolerance'])
    return spectra,directions
