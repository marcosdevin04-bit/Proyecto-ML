import os, sys, json, time
from pathlib import Path
root=Path(__file__).parent
from preparar_datos import preparar_datos
preparar_datos(root)
os.environ['JUPYTER_PATH']=str(root/'.jupyter')
os.environ['IPYTHONDIR']=str(root/'.ipython')
os.environ['JUPYTER_RUNTIME_DIR']=str(root/'.jupyter/runtime')
os.environ['MPLCONFIGDIR']=str(root/'.matplotlib')
os.environ['OMP_NUM_THREADS']='1'
os.environ['OPENBLAS_NUM_THREADS']='1'
os.environ['MKL_NUM_THREADS']='1'
kernel=root/'.jupyter/kernels/ose'
kernel.mkdir(parents=True,exist_ok=True)
(kernel/'kernel.json').write_text(json.dumps({'argv':[sys.executable,'-m','ipykernel_launcher','-f','{connection_file}'],
    'display_name':'OSE Python','language':'python'}),encoding='utf-8')
import nbformat
from nbclient import NotebookClient
notebook=root/'entrega_reclamos_ose.ipynb'
nb=nbformat.read(notebook,as_version=4)
nbformat.validate(nb)
for i,c in enumerate(nb.cells):
    if c.cell_type=='code':
        compile(c.source,f'celda-{i}','exec')
def comienzo(cell,cell_index,**kwargs):
    print(f'Celda {cell_index}: {cell.source.splitlines()[0][:100]}',flush=True)
def terminada(cell,cell_index,**kwargs):
    nbformat.write(nb,notebook)
cliente=NotebookClient(nb,timeout=1800,kernel_name='ose',resources={'metadata':{'path':str(root)}},
    on_cell_start=comienzo,on_cell_executed=terminada)
inicio=time.time()
try:
    cliente.execute()
finally:
    nbformat.write(nb,notebook)
print(f'Ejecución completa en {time.time()-inicio:.1f} s',flush=True)
