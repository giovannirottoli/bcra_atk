import streamlit as st
import pandas as pd
import requests as rq
import pprint
import locale


def get_situacion(situacion):
    d = {
        1: 'Normal',
        2: 'Seguimiento especial',
        3: 'Con problemas',
        4: 'Alto riesgo',
        5: 'Irrecuperable',    
    }
    return d.get(situacion, 'S/D')

def search(cuil):
    if len(cuil) != 11:
        st.error('Asegúrese de ingresar los 11 dígitos del CUIL', icon="🚨")
    elif not cuil.isnumeric():
        st.error('Asegúrese de ingresar sólo números, sin guiones ni espacios', icon="🚨")
    else:
        url = f"https://api.bcra.gob.ar/CentralDeDeudores/v1.0/Deudas/{cuil}"
        response = rq.get(url, verify=False)
        if response.status_code != 200:
            st.error(f'Error al obtener info desde el BCRA: ' + pprint.pformat(response.content), icon="🚨")
        else:
            
            j = response.json()
            j = j['results']
            
            total_adeudado = 0
            
            st.markdown(f'**Identificación:** { j.get("identificacion", "S/D") }')
            st.markdown(f'**Denominación:** {j.get("denominacion", "Sin datos")}')
            st.subheader("Períodos", divider=True)
            for periodo in  j.get('periodos', []):
                st.markdown(f'Período: {periodo.get("periodo")}')
                data = ""
                for entidad in periodo.get('entidades', []):
                    name = entidad.get('entidad', 'Sin Nombre')
                    fecha = entidad.get('fechaSit1', 'Sin Fecha')
                    monto = entidad.get('monto', 0) if entidad.get('monto', 0) else 0
                    
                    total_adeudado = total_adeudado + monto
                    
                    monto = locale.format_string("%d", monto*1000, grouping=True, monetary=True)
                    situacion = entidad.get('situacion', 'S/D')
                    situacion_exp = get_situacion(situacion)
                    atraso = entidad.get('diasAtrasoPago', '')

                    
                    line = f"{name if name else 'Sin Nombre'} - {fecha if fecha else 'Sin fecha'}: ${monto} - Situación {situacion} ({situacion_exp}) \n"
                    data = data + line

                st.code(data, language="json")
                st.divider()
                
                #st.code(pprint.pformat(j), language="json")
                
            st.info(f'**Total adeudado informado:** ${locale.format_string("%d", total_adeudado*1000, grouping=True, monetary=True)}')




def main():
    locale.setlocale(locale.LC_ALL, 'es_AR.utf8')
    st.title('Portal de deudas')
    
    text_input = st.text_input(
        "Ingrese 11 dígitos del CUIL 👇",
        label_visibility='visible',
        placeholder='Sin guiones ni espacios',
    )

    if text_input:
        search(text_input)
    
    
    footer = """<style>.footer {position: fixed;left: 0;bottom: 0;width: 100%;background-color: #000;color: white;text-align: center;}</style><div class='footer'><p>Hecho por Artekium Technology Studio</p></div>"""

    st.markdown(footer, unsafe_allow_html=True)
        
if __name__ == "__main__":main()
