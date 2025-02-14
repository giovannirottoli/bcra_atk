import streamlit as st
import pandas as pd
import requests as rq
import pprint
import locale


def get_situacion(situacion):
    d = {
        1: 'Sin atraso',
        2: 'Mora leve',
        3: 'Mora extendida',
        4: 'Mora Grave',
        5: 'Irrecuperable',    
    }
    return d.get(situacion, 'S/D')

def get_data(j):
    total_adeudado = 0
    data = []
    
    for periodo in  j.get('periodos', []):
        for entidad in periodo.get('entidades', []):
            
            entity = {}
            
            entity['name'] = entidad.get('entidad', 'S/D')
            entity['monto'] = entidad.get('monto', 0) if entidad.get('monto', 0) else 0
            entity['situacion'] = entidad.get('situacion', 'S/D')
            entity['situacion_exp'] = get_situacion(entity['situacion'])
            entity['periodo'] = periodo.get('periodo')
            total_adeudado = total_adeudado + entity['monto']
            
            data.append(entity)
    return sorted(data, key=lambda x: x['monto'], reverse=True)  , total_adeudado

def get_lines(data):
    lines = ""    
    for record in data: 
        monto = locale.format_string("%d", record['monto']*1000, grouping=True, monetary=True)
        periodo = record['periodo']
        if len(periodo) == 6:
            periodo = f"{periodo[4:]}/{periodo[2:4]}"
            
        line = f"Situación {record['situacion']} ({record['situacion_exp']}) -  ${monto} -  {record['name'] if record['name'] else 'Sin Nombre'} - {periodo} \n"                 
        lines = lines + line
        
    return lines

def search(cuil):
    if len(cuil) != 11:
        st.error('Asegúrese de ingresar los 11 dígitos del CUIL', icon="🚨")
    elif not cuil.isnumeric():
        st.error('Asegúrese de ingresar sólo números, sin guiones ni espacios', icon="🚨")
    else:
        url = f"https://api.bcra.gob.ar/CentralDeDeudores/v1.0/Deudas/{cuil}"
        response = rq.get(url, verify=False)
        
        if response.status_code == 500:
            st.error(f'Error al obtener info desde el BCRA por un problema interno \n ' + pprint.pformat(response.content), icon="🚨")
        if response.status_code == 400:
            st.error(f"Parámetro erróneo: Ingresar 11 dígitos para realizar la consulta.", icon="🚨")
        if response.status_code == 404:
            st.info(f"No se encuentran deudas para el CUIL especificado: {cuil}", icon="🕵️‍♂️" )
        else:
            j = response.json()
            j = j['results']
                        
            data, total_adeudado = get_data(j)
            
            total_adeudado = locale.format_string("%d", total_adeudado*1000, grouping=True, monetary=True)
            lines = get_lines(data) + f"Total adeudado informado: ${total_adeudado}"
            
            col_1, col_2 = st.columns(2)
            row2 = st.container()
            
            with col_1:
                st.markdown(f'**Identificación:** { j.get("identificacion", "S/D") }')
                st.markdown(f'**Denominación:** {j.get("denominacion", "Sin datos")}')
            with col_2:
                st.metric(label="Total adeudado", value=f"$ {total_adeudado}")
            with row2:
                st.subheader("Deudas informadas", divider=True)
            
                st.code(lines, language="json")
            



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
