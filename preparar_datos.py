"""Extrae el CSV oficial incluido en data/ose_2024.zip, sin descarga adicional."""
from pathlib import Path
import shutil
import zipfile

def preparar_datos(raiz=None):
    raiz=Path(raiz) if raiz is not None else Path(__file__).resolve().parent
    destino=raiz/'data'/'solicitudes_reclamos_operativos_2024.csv'
    if destino.exists():
        print('CSV de OSE disponible:', destino.name)
        return destino
    archivo=raiz/'data'/'ose_2024.zip'
    if not archivo.exists():
        raise FileNotFoundError(f'Falta {archivo}. Obtener los datos de https://datos.ose.com.uy/dataset/reclamos-operativos')
    with zipfile.ZipFile(archivo) as z:
        candidatos=[i for i in z.infolist() if not i.is_dir() and Path(i.filename).name==destino.name]
        if len(candidatos)!=1:
            raise ValueError('El ZIP debe contener exactamente un CSV oficial de 2024')
        destino.parent.mkdir(parents=True,exist_ok=True)
        # Se usa un nombre fijo, sin extraer rutas arbitrarias del ZIP.
        with z.open(candidatos[0]) as origen, destino.open('wb') as salida:
            shutil.copyfileobj(origen,salida)
    print('CSV de OSE extraído:',destino.name,'| bytes:',destino.stat().st_size)
    return destino

if __name__=='__main__':
    preparar_datos()
