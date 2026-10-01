import datetime
from datetime import datetime, timedelta
import os
import threading
import pandas as pd
from openpyxl import Workbook, load_workbook
from decoder_gt06V4 import *
from datetime import datetime, timedelta

DECODED_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "decoded")

DECODED_COLUMNS = [
    "Data/Hora Inclusão", "Data/Hora Evento", "IMEI", "Sequência",
    "Tipo Mensagem", "Tipo Dispositivo", "Versão Protocolo", "Versão Firmware",
    "Alimentação Externa", "Bateria interna interna", "Analog Input Status",
    "Satélites", "Duração da Ignição",
    "Velocidade", "Azimuth", "Latitude", "Longitude", "MCC", "MNC", "LAC", "Cell ID",
    "Realtime positioning", "GPS valido",
    "Hodômetro Total", "Horímetro Total",
    "Tipo de Rede", "Qualidade do sinal de GSM", "Terminal information",
    "Carregamento", "Funcionamento", "Alarmes internos", "Rastreamento", "Gás/Oléo"
]

_excel_lock = threading.Lock()
_printed_write_errors = set()

def _print_write_error_once(file_name, error):
    key = f"{file_name}:{error}"
    if key not in _printed_write_errors:
        _printed_write_errors.add(key)
        print(f"Erro ao escrever no arquivo {file_name}: {error}")

def _normalize_msg(msg):
    if isinstance(msg, dict):
        return msg.get("dados", "")
    return str(msg)

def _build_row(timestamp_inclusao, msg):
    if timestamp_inclusao:
        date_time_inclusao = timestamp_inclusao
    else:
        date_time_inclusao = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]

    dados = _normalize_msg(msg)
    fields = dados.split(",") if dados else []
    row = [date_time_inclusao] + fields

    while len(row) < len(DECODED_COLUMNS):
        row.append("")
    return row[:len(DECODED_COLUMNS)]

def _append_to_excel(file_name, row):
    with _excel_lock:
        if os.path.exists(file_name):
            wb = load_workbook(file_name)
            ws = wb.active
            ws.append(row)
            wb.save(file_name)
            wb.close()
        else:
            wb = Workbook()
            ws = wb.active
            ws.append(DECODED_COLUMNS)
            ws.append(row)
            wb.save(file_name)
            wb.close()

def record_raw(file_name, source, msg):
    curr_time = datetime.now()
    date_time = curr_time.strftime("%Y-%m-%d %H:%M:%S,")
    with open(file_name, "a+") as f:
        f.write(date_time + source + ',' + msg + "\n")
        f.close()

def record_decoded_by_imei_with_timestamp(imei, msg, timestamp_inclusao=None):

    # Cria o nome do arquivo baseado no IMEI
    file_name = f"{imei}_decoded.csv"
    
    try:
        # Verifica se o arquivo já existe
        if os.path.exists(file_name):
            # Se existe, apenas adiciona os dados
            with open(file_name, "a+", encoding='utf-8') as d:
                # Use o timestamp fornecido ou o atual
                if timestamp_inclusao:
                    date_time_inclusao = timestamp_inclusao
                else:
                    curr_time = datetime.now()
                    date_time_inclusao = curr_time.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]

                
                d.write(f"{date_time_inclusao},{msg}\n")
        else:
            # Se não existe, cria o arquivo com cabeçalho
            # print(f"Criando novo arquivo de log para IMEI: {imei}")
            with open(file_name, "w", encoding='utf-8') as d:
                # Escreve o cabeçalho
                d.write("Data/Hora Inclusão,Data/Hora Evento,IMEI,Sequência,"
                        "Tipo Mensagem,Tipo Dispositivo,Versão Protocolo,Versão Firmware,"
                        "Alimentação Externa,Bateria interna interna,Analog Input Status,"
                        "Satélites,Duração da Ignição,"
                        "Velocidade,Azimuth,Latitude,Longitude,MCC,MNC,LAC,Cell ID,Realtime positioning,GPS valido,"
                        "Hodômetro Total,Horímetro Total,"
                        "Tipo de Rede,Qualidade do sinal de GSM,Terminal information,Carregamento,Funcionamento,Alarmes internos,Rastramento,Gás/Oléo\n")
                
                # Adiciona o primeiro registro
                # Use o timestamp fornecido ou o atual
                if timestamp_inclusao:
                    date_time_inclusao = timestamp_inclusao
                else:
                    curr_time = datetime.now()
                    date_time_inclusao = curr_time.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]

                
                d.write(f"{date_time_inclusao},{msg}\n")
                
    except Exception as e:
        _print_write_error_once(file_name, e)

def record_decoded_by_imei(imei, msg):
    """
    Função original mantida para compatibilidade
    """
    record_decoded_by_imei_with_timestamp(imei, msg, None)

def record_decoded(file_name, msg, imei=None, timestamp_inclusao=None):
    """
    Função original mantida para compatibilidade
    Se imei for fornecido, usa a nova função
    """
    if imei:
        record_decoded_by_imei_with_timestamp(imei, msg, timestamp_inclusao)
        return
    
    # Código original
    try:
        open(file_name, "r")
        with open(file_name, "a+") as d:
            # Use o timestamp fornecido ou o atual
            if timestamp_inclusao:
                date_time = timestamp_inclusao + ","
            else:
                curr_time = datetime.now()
                date_time = curr_time.strftime("%Y-%m-%d %H:%M:%S,")
            
            d.write(date_time + msg + "\n")
            d.close()
    except:
        # print("Arquivo não existe, um novo log será criado.")
        with open(file_name, "a+") as d:
            d.write("Data/Hora Inclusão,Data/Hora Evento,IMEI,Sequência,"
                        "Tipo Mensagem,Tipo Dispositivo,Versão Protocolo,Versão Firmware,"
                        "Alimentação Externa,Bateria interna interna,Analog Input Status,"
                        "Satélites,Duração da Ignição,"
                        "Velocidade,Azimuth,Latitude,Longitude,MCC,MNC,LAC,Cell ID,Realtime positioning,GPS valido,"
                        "Hodômetro Total,Horímetro Total,"
                        "Tipo de Rede,Qualidade do sinal de GSM,Terminal information,Carregamento,Funcionamento,Alarmes internos,Rastramento,Gás/Oléo\n")

            # Use o timestamp fornecido ou o atual
            if timestamp_inclusao:
                date_time = timestamp_inclusao
            else:
                curr_time = datetime.now()
                date_time = curr_time.strftime("%Y-%m-%d %H:%M:%S")
            
            d.write(f"{date_time},{msg}\n")
            d.close()


def record_decoded_organized_with_timestamp(imei, msg, timestamp_inclusao=None):
    """
    Versão organizada que salva na pasta decoded/ em formato Excel (.xlsx)
    """
    os.makedirs(DECODED_DIR, exist_ok=True)
    file_name = os.path.join(DECODED_DIR, f"{imei}_decoded.xlsx")

    try:
        row = _build_row(timestamp_inclusao, msg)
        _append_to_excel(file_name, row)
        return True
    except Exception as e:
        _print_write_error_once(file_name, e)
        return False


def record_decoded_organized(imei, msg):
    """
    Versão organizada que salva na pasta decoded/ em formato Excel (.xlsx)
    """
    return record_decoded_organized_with_timestamp(imei, msg, None)


def record_combined_message_with_timestamp(file_name, direction, msg_type, hex_data, timestamp_inclusao=None):
    """Grava mensagem no arquivo combinado com timestamp personalizado"""
    try:
        # Use o timestamp fornecido ou o atual
        if timestamp_inclusao:
            date_time = timestamp_inclusao
        else:
            curr_time = datetime.now()
            date_time = curr_time.strftime("%Y-%m-%d %H:%M:%S")
        
        with open(file_name, "a+", encoding='utf-8') as f:
            f.write(f"{date_time},{direction},{msg_type},{hex_data}\n")
    except Exception as e:
        print(f"Erro ao gravar mensagem combinada: {e}")

def record_combined_message(file_name, direction, msg_type, hex_data):
    """Versão original mantida para compatibilidade"""
    record_combined_message_with_timestamp(file_name, direction, msg_type, hex_data, None)

def hex_to_timestamp(hex_value):
    hex_value = str(hex_value)

    try:
        if len(hex_value) == 12:
            # Formato padrão: 6 bytes (YYMMDDHHMMSS)
            year = 2000 + int(hex_value[0:2], 16)
            month = int(hex_value[2:4], 16)
            day = int(hex_value[4:6], 16)
            hour = int(hex_value[6:8], 16)
            minute = int(hex_value[8:10], 16)
            second = int(hex_value[10:12], 16)

        elif len(hex_value) == 14:
            # Formato alternativo: 7 bytes (YYYYMMDDHHMMSS)
            year = int(hex_value[0:4], 16)
            month = int(hex_value[4:6], 16)
            day = int(hex_value[6:8], 16)
            hour = int(hex_value[8:10], 16)
            minute = int(hex_value[10:12], 16)
            second = int(hex_value[12:14], 16)

        else:
            # Formato inválido
            raise ValueError("Tamanho inválido de string hexadecimal para data/hora.")

        # Validação segura de data
        dt = datetime(year, month, day, hour, minute, second)

    except Exception:
        # Fallback seguro
        dt = datetime(2020, 1, 1, 0, 0, 0)

    return dt

def converter_para_brasil(dt_utc):
    """
    Converte uma data/hora UTC (string ou datetime) para o timezone do Brasil (UTC-3)
    e retorna no formato 'YYYY-MM-DD HH:MM:SS.mmm' (com milissegundos).
    """

    # Se for string, tenta converter
    if isinstance(dt_utc, str):
        formatos = [
            "%Y%m%d%H%M%S",        # 20250408223920
            "%Y-%m-%d %H:%M:%S",   # 2025-04-08 22:39:20
            "%y-%m-%d %H:%M:%S",   # 25-04-08 22:39:20
            "%Y-%m-%d %H:%M:%S.%f" # 2025-04-08 22:39:20.123456
        ]
        for formato in formatos:
            try:
                dt_utc = datetime.strptime(dt_utc, formato)
                break
            except ValueError:
                continue
        else:
            return f"Erro: Não foi possível converter '{dt_utc}' para datetime"

    # Se ainda não for datetime, erro
    if not isinstance(dt_utc, datetime):
        return f"Erro: Tipo inválido para conversão ({type(dt_utc)})"

    # Ajuste fuso horário UTC -> Brasil (UTC-3)
    dt_brasil = dt_utc - timedelta(hours=3)

    # Retorna com milissegundos
    return dt_brasil.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]

def separar_partes_comando(command_string):
    # Verifica se existe o caracter ":" na string
    if ":" in command_string:
        # Divide a string no primeiro ":" encontrado
        partes = command_string.split(":", 1)
        primeira_parte = partes[0]  # Parte antes do ":"
        segunda_parte = partes[1]  # Parte depois do ":"

        # Verifica se a primeira parte existe (não está vazia)
        if primeira_parte.strip() == "":
            return False, "Primeira parte está vazia", "", ""

        # Verifica se a primeira parte é um número válido diferente de zero
        try:
            numero = int(primeira_parte)
            if numero == 0:
                return False, "Número antes do ':' é zero", primeira_parte, segunda_parte
            else:
                return True, "Primeira parte válida", primeira_parte, segunda_parte
        except ValueError:
            return False, "Primeira parte não é um número válido", primeira_parte, segunda_parte
    else:
        # Retorna erro se não encontrar ":"
        return False, "Comando não contém o caracter ':'", "", ""

def process_gt06_folder(input_path, output_path):
    
    # Cria pasta de saída se não existir
    if not os.path.exists(output_path):
        os.makedirs(output_path)
    
    # Valida pasta de entrada
    if not os.path.exists(input_path) or not os.path.isdir(input_path):
        print(f"Erro: Pasta de entrada inválida: {input_path}")
        return False
    
    # Lista arquivos CSV
    csv_files = [f for f in os.listdir(input_path) 
                 if f.endswith('.csv') and not f.endswith('_decoded.csv')]
    
    if not csv_files:
        print("Aviso: Nenhum arquivo CSV encontrado na pasta")
        return False
    
    total_files = len(csv_files)
    processed_files = 0
    
    # Processa cada arquivo CSV
    for csv_file in csv_files:
        input_file = os.path.join(input_path, csv_file)
        file_imei = os.path.splitext(csv_file)[0]
        
        # Remove zero à esquerda se existir
        if file_imei.startswith('0') and len(file_imei) == 16:
            file_imei = file_imei[1:]
        
        output_file = os.path.join(output_path, f"{file_imei}_decoded.xlsx")
        
        try:
            # Lê o arquivo CSV
            df = pd.read_csv(input_file)
            
            # Verifica colunas obrigatórias
            if 'lmsmensagem' not in df.columns or 'lmsdatahorainc' not in df.columns:
                print(f"Erro: Colunas obrigatórias não encontradas em {csv_file}")
                continue
            
            # Remove linhas vazias
            df_clean = df.dropna(subset=['lmsmensagem'])
            df_clean = df_clean[df_clean['lmsmensagem'].str.strip() != '']
            
            total_rows = len(df)
            valid_rows = len(df_clean)
            
            # Remove arquivo de saída se existir
            if os.path.exists(output_file):
                os.remove(output_file)
            
            # Processa cada linha
            for index, row in df_clean.iterrows():
                try:
                    hex_message = str(row['lmsmensagem']).strip().strip('"\'')
                    timestamp_inc = str(row['lmsdatahorainc']).strip()
                    hex_data = hex_message.replace(" ", "").upper()
                    
                    # Valida hexadecimal
                    if not (hex_data and len(hex_data) % 2 == 0):
                        try:
                            int(hex_data, 16)
                        except ValueError:
                            continue
                    
                    # Formata timestamp
                    formatted_timestamp = timestamp_inc
                    for fmt in ["%Y-%m-%d %H:%M:%S.%f", "%Y-%m-%d %H:%M:%S", 
                               "%d/%m/%Y %H:%M:%S", "%Y/%m/%d %H:%M:%S"]:
                        try:
                            dt = datetime.strptime(timestamp_inc, fmt)
                            formatted_timestamp = dt.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
                            break
                        except ValueError:
                            continue
                    
                    # Analisa mensagem usando o parser
                    if hex_data.startswith("7878") and hex_data.endswith("0D0A"):
                        try:
                            # Chama o parser para processar a mensagem
                            result = parser_gt06V4(hex_data, file_imei, formatted_timestamp)
                            
                            # CORREÇÃO: Extrai a string 'dados' do dicionário retornado pelo parser
                            if result and 'dados' in result:
                                dados_string = result['dados']
                                
                                # Grava usando a função organizada
                                record_decoded_organized_with_timestamp(file_imei, dados_string, formatted_timestamp)
                            else:
                                # Se não retornou dados válidos, cria uma entrada básica
                                dados_basicos = f",{file_imei},,,Protocolo não decodificado,,,,,,,,,,,,,,,,,,,,,,,"
                                record_decoded_organized_with_timestamp(file_imei, dados_basicos, formatted_timestamp)
                                
                        except Exception as e:
                            print(f"Erro no parser para mensagem {hex_data}: {e}")
                            # Em caso de erro, grava uma entrada de erro
                            dados_erro = f",{file_imei},,,Erro no parser: {str(e)},,,,,,,,,,,,,,,,,,,,,,,"
                            record_decoded_organized_with_timestamp(file_imei, dados_erro, formatted_timestamp)
                            continue
                
                except Exception as e:
                    print(f"Erro ao processar linha: {e}")
                    continue
            
            processed_files += 1
            print(f"Processado: {csv_file} -> {os.path.basename(output_file)}")
        
        except Exception as e:
            print(f"Erro ao processar {csv_file}: {e}")
    print("Processamento concluído")

    # print(f"Processamento concluído: {processed_files}/{total_files} arquivos processados")
    return True


# Exemplo de uso
if __name__ == "__main__":
    input = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logs")
    output = DECODED_DIR
    # Processa a pasta
    process_gt06_folder(input, output)