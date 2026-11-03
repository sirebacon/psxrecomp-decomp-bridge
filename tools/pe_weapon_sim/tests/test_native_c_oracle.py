"""Compare Python arithmetic against the native C damage helper, compiled unchanged."""
import _ctypes,ctypes,random,re,subprocess,tempfile,unittest
from pathlib import Path
from pe_weapon_sim.native_damage import hit_damage,VANILLA_SHOT_PCT
from pe_weapon_sim import rules
class NativeCOracleTests(unittest.TestCase):
    def test_native_helper_randomized(self):
        root=Path('D:/Recomp Games/parasite-eve-pc')
        cc=Path('C:/Users/maver/.local/share/retcomm/toolchains/cmake-clang-v1/latest/bin/clang.exe')
        if not root.exists() or not cc.exists():self.skipTest('Native checkout/toolchain not available')
        text=(root/'mods/pe_rebalance/pe_mod_effects.c').read_text()
        body=re.search(r'static int pe_hit_damage\(.*?\n\}',text,re.S)[0]
        harness='#include <stdint.h>\nstatic const uint8_t s_shot_pct[11]={0,100,60,41,0,25,0,18,0,0,13};\n'+body
        harness+='\n__declspec(dllexport) int oracle(int s,int p,unsigned n,unsigned d,uint32_t flags){return pe_hit_damage(s,p,n,d,flags,0,0);}\n'
        with tempfile.TemporaryDirectory(prefix='pe-native-oracle-') as tmp:
            c=Path(tmp)/'oracle.c';dll=Path(tmp)/'oracle.dll';c.write_text(harness)
            subprocess.run([str(cc),'-shared','-O2',str(c),'-o',str(dll)],check=True,capture_output=True)
            lib=ctypes.CDLL(str(dll));fn=lib.oracle;fn.argtypes=[ctypes.c_int,ctypes.c_int,ctypes.c_uint,ctypes.c_uint,ctypes.c_uint];fn.restype=ctypes.c_int
            r=dict(rules.CURRENT,rof_mod_hit_pct={5:40,7:29,10:20});rng=random.Random(26)
            reactions={'graze':0x8000,'hit':0x10000,'crit':0x18000,'splash':0x20000}
            for _ in range(2000):
                offense=rng.randrange(0,1000);power=rng.randrange(0,1000);defense=rng.randrange(0,300);shots=rng.choice(list(VANILLA_SHOT_PCT));reaction=rng.choice(list(reactions));element=rng.choice([80,100,115,150]);installed=rng.choice([False,True])
                s=offense//5;p=VANILLA_SHOT_PCT[shots]
                pm=200000//(shots*p) if installed and shots in (5,7,10) else r['hit_pct'][shots]*1000//p
                want=max(0,((s+power)*pm//1000)*(element*10)//1000-s)
                expected=fn(s,min(32767,want),shots,defense*element//100,reactions[reaction])
                self.assertEqual(hit_damage(offense,power,defense,shots,reaction,element,r,installed),expected)
            _ctypes.FreeLibrary(lib._handle)
if __name__=='__main__':unittest.main()
