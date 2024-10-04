git clone https://github.com/p4lang/behavioral-model.git
cd behavioral-model/

# version 1.15.0 (Feb 10, 2022)
git checkout f745e1db5e281d1e30483496c3c0960a8d23c852
echo "Updating BMV2 files"

\cp ../compression-files/fields.h include/bm/bm_sim/
\cp ../compression-files/fields.cpp src/bm_sim/
\cp ../compression-files/primitives.cpp targets/simple_switch/

cd ../
echo "Updating P4C files"

git clone --recursive https://github.com/p4lang/p4c.git
cd p4c
# version 1.2.3.0 (Aug 2, 2022)
git checkout 1576090b74b610e979a3afeafec79d0a2f81a598
# clona submódulos necessários!! (sem esse comando, ocorrem erros na compilação)
git submodule update --init --recursive

\cp ../compression-files/simpleSwitch.cpp  backends/bmv2/simple_switch/
\cp ../compression-files/simpleSwitch.h  backends/bmv2/simple_switch/
\cp ../compression-files/programStructure.cpp frontends/p4/fromv1.0/
\cp ../compression-files/v1model.h frontends/p4/fromv1.0/
\cp ../compression-files/v1model.p4 p4include/
\cp p4include/v1model.p4 /usr/share/p4c/p4include

mkdir build
