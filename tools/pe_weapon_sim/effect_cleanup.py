"""FieldFx_UpdateTasks script-before-callback cleanup semantics."""
from dataclasses import dataclass

@dataclass
class EffectCleanup:
    spawn_update:int
    stop_gate_update:int
    controller_end_update:int
    live:bool=False
    finished:bool=False
    last_update:int=0

    def step(self,update,*,result=None,pool_active_before=0):
        if update!=self.last_update+1:raise ValueError('nonconsecutive effect update')
        self.last_update=update
        if self.finished:return True
        # Task script opcode0 sees the count before callbacks execute.
        if update>=self.stop_gate_update and not self.live:
            self.finished=True;return True
        if update==self.spawn_update:self.live=True
        if self.live:
            if result is None:result=1 if update>=self.controller_end_update else 0
            if result==1 or result==2 and pool_active_before==0:self.live=False
        return False
