"""Regla prospectiva de rachas, independiente de SciPy y del objetivo."""
class SustainedRule:
    def __init__(self,interval,required,threshold):
        self.interval=interval;self.required=required;self.threshold=threshold
        self.last=None;self.streak=0;self.requested=False;self.stop_iteration=None
    def observe(self,iteration,verified,kkt):
        if iteration==0:return False
        if iteration<0 or iteration%self.interval:raise ValueError('unscheduled audit')
        if self.last is not None and iteration-self.last!=self.interval:self.streak=0
        self.streak=self.streak+1 if verified and kkt<=self.threshold else 0
        self.last=iteration
        if self.streak>=self.required:self.requested=True;self.stop_iteration=iteration
        return self.requested

def controls():
    r=SustainedRule(200,3,1e-5);assert not r.observe(0,True,0) and r.streak==0
    assert not r.observe(200,True,0) and not r.observe(400,True,0) and r.observe(600,True,0)
    for bad_verified,bad_kkt in [(True,1e-3),(False,0.)]:
        r=SustainedRule(200,3,1e-5)
        for iteration,verified,kkt in [(200,True,0.),(400,bad_verified,bad_kkt),(600,True,0.),(800,True,0.)]:assert not r.observe(iteration,verified,kkt)
        assert r.observe(1000,True,0.)
    r=SustainedRule(200,3,1e-5);r.observe(200,True,0.);r.observe(600,True,0.);assert r.streak==1
    return True
