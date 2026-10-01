from recordMessages import hex_to_timestamp, converter_para_brasil
from datetime import timedelta

def _print_result(result):
    if not result:
        return
    print(f"Tipo_mensagem: {result.get('tipo', result.get('message_type', ''))}")
    for key, value in result.items():
        if key in ('tipo', 'message_type'):
            continue
        print(f"{key}: {value}")

def decode_course_info(course_hex):
    course_MSB = int(course_hex[0:2], 16)
    course_LSB = int(course_hex[2:4], 16)

    msb_bin = bin(course_MSB)[2:].zfill(8)
    lsb_bin = bin(course_LSB)[2:].zfill(8)

    course_bin = msb_bin + lsb_bin
    
    realtime_gps = int(course_bin[2])
    gps_posicionado = int(course_bin[3])
    longitude_leste = int(course_bin[4])
    latitude_norte = int(course_bin[5])

    course_bits = course_bin[6:16]
    azimute = int(course_bits, 2)
    
    return {
        'azimute': azimute,
        'realtime_gps': realtime_gps,
        'gps_posicionado': gps_posicionado,
        'longitude_leste': longitude_leste,
        'latitude_norte': latitude_norte,
        'course_bin': course_bin,
        'course_bits': course_bits
    }

def apply_coordinate_signs(latitude, longitude, course_info):
    """Aplica os sinais corretos à latitude e longitude"""
    if course_info['latitude_norte'] == 0: 
        latitude = -latitude
    
    if course_info['longitude_leste'] == 1:
        longitude = -longitude
        
    return latitude, longitude

def parser_gt06V4(hex_data, imei=None, timestamp_inclusao=None):
    """
    Parser GT06V4 que retorna dicionário com dados decodificados
    
    Args:
        hex_data: dados hexadecimais da mensagem
        imei: IMEI do dispositivo
        timestamp_inclusao: timestamp personalizado do CSV (opcional)
        
    Returns:
        dict: dicionário com dados decodificados ou None em caso de erro
    """
    protocol_number = hex_data[6:8]

    try:
        if protocol_number == "01":  # Login
            Tipo_mensagem = "Login"
            p = 4
            length = hex_data[p:p+2]
            p += 2
            protocol_number = hex_data[p:p+2]
            p += 2
            imei_raw = hex_data[p:p+16]
            
            if imei_raw.startswith('0') and len(imei_raw) == 16:
                imei = imei_raw[1:]
            else:
                imei = imei_raw
            p += 16
            serial_number = hex_data[p:p+4]
            serial_number = int(serial_number, 16)
            p += 4
             
            print(f"\n")
            print(f"Tipo_mensagem: {Tipo_mensagem}") 
            print(f"Serial number: {serial_number}") 
            print(f"IMEI: {imei}")
            print(f"Protocol number: {protocol_number}")
            print(f"Length: {length}")
            print(f"\n\n")


            result = {
                'tipo': Tipo_mensagem,
                'imei': imei,
                'serial': serial_number,
                'message_type': Tipo_mensagem,
                'protocol': 'GT06',
                'dados': f",{imei},{serial_number},{Tipo_mensagem},77,GT06V4,,,," + ",,,,,,,"
            }
            #_print_result(result)
            return result

        elif protocol_number == "13":  # Heartbeat
            Tipo_mensagem = "Heartbeat"
            p = 4
            length = hex_data[p:p+2]
            p += 2
            protocol_number = hex_data[p:p+2]
            p += 2
            terminal_info = hex_data[p:p+2]
            p += 2
            external_power = hex_data[p:p+2]
            p += 2
            gsm_signal = hex_data[p:p+2]
            p += 2
            alarm = hex_data[p:p+4]
            p += 4
            serial_number = hex_data[p:p+4]
            serial_number = int(serial_number, 16)
            p += 4
            
            external_power = str(external_power)
            
            if external_power == '00':
                external_power = "Sem bateria"
            elif external_power == '01':
                external_power = "Bateria extremamente baixa"
            elif external_power == '02':
                external_power = "Bem baixa bateria"
            elif external_power == '03':
                external_power = "Bateria baixa"
            elif external_power == '04':
                external_power = "Bateria média"
            elif external_power == '05':
                external_power = "Bateria alta"
            elif external_power == '06':
                external_power = "Bateria extremamente alta"
            else: 
                external_power = "Desconhecido"

            print(f"\n")
            print(f"Tipo_mensagem: {Tipo_mensagem}") 
            print(f"Alarm: {alarm}")
            print(f"Serial number: {serial_number}") 
            print(f"Protocol number: {protocol_number}")
            print(f"Length: {length}")
            print(f"External power: {external_power}")
            print(f"GSM signal: {gsm_signal}")
            print(f"\n\n")
         

            result = {
                'tipo': Tipo_mensagem,
                'imei': imei,
                'serial': serial_number,
                'message_type': Tipo_mensagem,
                'protocol': 'GT06',
                'power': external_power,
                'gsm': gsm_signal,
                'dados': f",{imei},{serial_number},{Tipo_mensagem},77,GT06V4,,,{external_power}," + f",,,,,,,,,,,,,,,,{gsm_signal}"
            }
           # _print_result(result)
            return result
       
        elif protocol_number == "32":  # GPS Data
            p = 4
            length = hex_data[p:p+2]
            p += 2 
            protocol_number = hex_data[p:p+2]
            p += 2  
            send_time = hex_data[p:p+12]
            send_time_utc = hex_to_timestamp(send_time)
            p += 12 
            gps = hex_data[p:p+2]
            satelites_in_use = int(str(gps[1]), 16)
            p += 2
            latitude = hex_data[p:p+8]
            latitude = int(latitude, 16) / 1800000
            p += 8
            longitude = hex_data[p:p+8]
            longitude = int(longitude, 16) / 1800000
            p += 8
            speed = hex_data[p:p+2]
            speed = int(speed, 16) 
            p += 2
            
            course = hex_data[p:p+4]
            course_info = decode_course_info(course)
            
            latitude, longitude = apply_coordinate_signs(latitude, longitude, course_info)
            
            p += 4
            mcc = hex_data[p:p+4]
            p += 4
            mnc = hex_data[p:p+2]
            p += 2
            lac = hex_data[p:p+4]   
            p += 4
            cell_id = hex_data[p:p+8]
            p += 8
            acc = hex_data[p:p+2]
            acc = int(acc, 16) 
            p += 2
            data_up = hex_data[p:p+2]
            p += 2
            gps_real = hex_data[p:p+2]
            p += 2
            milage = hex_data[p:p+8]
            milage = int(milage, 16) / 1000
            p += 8
            external_power = hex_data[p:p+4]
            external_power = int(external_power, 16)* 0.01
            external_power = float(external_power)
            external_power_str = f"{external_power:.2f}" 
            p += 4
            acc_on_time = hex_data[p:p+8]
            acc_on_time = int(acc_on_time, 16) 
            tempo = timedelta(seconds=acc_on_time)
            dias = tempo.days
            horas, resto = divmod(tempo.seconds, 3600)
            minutos, segundos = divmod(resto, 60)
            tempo_formatado = f"{dias:02d}-{horas:02d}:{minutos:02d}:{segundos:02d}"

            p += 8
            rat = hex_data[p:p+4]
            p += 4
            rat_prefix = rat[:1]
            rat_suffix = int(rat[1:], 16)
            serial_number = hex_data[p:p+4]
            serial_number = int(serial_number, 16) 
            p += 4
            
            
            if acc == 0:
                Tipo_mensagem = "Modo econômico"
            elif acc == 1:
                Tipo_mensagem = "Posicionamento por tempo em movimento"
            
            dados = f"{converter_para_brasil(send_time_utc)},{imei},{serial_number},{Tipo_mensagem},77,GT06V4,{rat_suffix},{external_power_str},," \
                    f"{acc},{satelites_in_use},,{speed},{course_info['azimute']},{latitude:.6f},{longitude:.6f},{mcc},{mnc},{lac},{cell_id},{course_info['realtime_gps']},{course_info['gps_posicionado']},{milage},{tempo_formatado},{rat_prefix},"

            print(f"Tipo_mensagem: {Tipo_mensagem}") 
            print(f"Serial number: {serial_number}") 
            print(f"Protocol number: {protocol_number}")
            print(f"Length: {length}")
            print(f"External power: {external_power_str}")
            print(f"Acc: {acc}")
            print(f"Satellites in use: {satelites_in_use}")
            print(f"Speed: {speed}")
            print(f"Course: {course_info['azimute']}")
            print(f"Lat/Lon: {latitude:.6f}, {longitude:.6f}")
            print(f"MCC: {mcc}")
            print(f"MNC: {mnc}")
            print(f"LAC: {lac}")
            print(f"Cell id: {cell_id}")
            print(f"Realtime GPS: {course_info['realtime_gps']}")
            print(f"GPS posicionado: {course_info['gps_posicionado']}")
            print(f"Milage: {milage}")
            print(f"Tempo formatado: {tempo_formatado}")
            print(f"\n\n")

            result = {
                'tipo': Tipo_mensagem,
                'imei': imei,
                'serial': serial_number,
                'message_type': Tipo_mensagem,
                'protocol': 'GT06',
                'latitude': latitude,
                'longitude': longitude,
                'speed': speed,
                'dados': dados
            }
            _print_result(result)
            return result

        elif protocol_number == "16":  # GPS Data with Alarm
            p = 4  
            length = hex_data[p:p+2]
            p += 2  
            protocol_number = hex_data[p:p+2]
            p += 2
            send_time = hex_data[p:p+12]
            send_time_utc = hex_to_timestamp(send_time)
            p += 12
            gps = hex_data[p:p+2]
            satelites_in_use = int(str(gps[0]), 16)
            p += 2
            latitude = hex_data[p:p+8]
            latitude = int(latitude, 16) / 1800000
            p += 8
            longitude = hex_data[p:p+8]
            longitude = int(longitude, 16) / 1800000
            p += 8
            speed = hex_data[p:p+2]
            speed = int(speed, 16)
            p += 2
            
            course = hex_data[p:p+4]
            course_info = decode_course_info(course)
            
            latitude, longitude = apply_coordinate_signs(latitude, longitude, course_info)
            
            p += 4
            LBS_Len = hex_data[p:p+2]
            p += 2
            mcc = hex_data[p:p+4]
            p += 4
            mnc = hex_data[p:p+2]
            p += 2
            lac = hex_data[p:p+4]
            p += 4
            cell_id = hex_data[p:p+6]
            p += 6
            terminal_status = hex_data[p:p+2]
            terminal_status = bin(int(terminal_status, 16))[2:].zfill(8)
            normal_working = terminal_status[7]
            acc_status = terminal_status[6]
            charging_status = terminal_status[5]
            alarm_status = terminal_status[2:5]
            gps_status = terminal_status[1]
            gas_oil_status = terminal_status[0]
            
            if normal_working == '1':
                normal_working = "Normal"
            elif normal_working == '0':
                normal_working = "Desativado"
            if acc_status == '1':
                acc = '1'
            elif acc_status == '0':
                acc = '0'
            if charging_status == '1':
                charging_status = "Carregamento on"
            elif charging_status == '0':
                charging_status = "Carregamento off"
            if alarm_status == '000':  
                alarm_status = "Normal"
            elif alarm_status == '001':
                alarm_status = "Shock alarm"
            elif alarm_status == '010':
                alarm_status = "Power cut alarm"
            elif alarm_status == '011':
                alarm_status = "Low battery alarm"
            elif alarm_status == '100':
                alarm_status = "SOS alarm"
            if gps_status == '1':
                gps_status = "Rastreamento de GPS ativo"
            elif gps_status == '0':
                gps_status = "Rastreamento de GPS inativo"
            if gas_oil_status == '1':
                gas_oil_status = "Gás/oléo e eletricidade ativo"
            elif gas_oil_status == '0':
                gas_oil_status = "Oléo e eletricidade inativo"

            p += 2
            external_power = hex_data[p:p+2]
            p += 2
            gsm_signal = hex_data[p:p+2]
            p += 2
            alarm = hex_data[p:p+4] 
            p += 4
            # milage = hex_data[p:p+8]
            # milage = int(milage, 16) / 1000
            # p += 8
            serial_number = hex_data[p:p+4]
            serial_number = int(serial_number, 16) 
            p += 4
            
            alarm_str = str(alarm)
            alarm_prefix = alarm_str[:2]
            if alarm_prefix == "01":
                Tipo_mensagem = "Alerta de Pânico"
            elif alarm_prefix == "02":
                Tipo_mensagem = "Desconexão de bateria"
            elif alarm_prefix == "06":
                Tipo_mensagem = "Excesso de velocidade"
            elif alarm_prefix == "16":
                Tipo_mensagem = "Retorno de velocidade"
            elif alarm_prefix == "F2":
                Tipo_mensagem = "Suspeita de acidente"
            elif alarm_prefix == "F3":
                Tipo_mensagem = "Bloqueio"
            elif alarm_prefix == "F4":  
                Tipo_mensagem = "Desbloqueio"
            elif alarm_prefix == "FE":
                Tipo_mensagem = "IGN"
            elif alarm_prefix == "FF":
                Tipo_mensagem = "IGF"

            external_power = str(external_power)
            if external_power == '00':
                external_power = "Sem bateria"
            elif external_power == '01':
                external_power = "Bateria extremamente baixa"
            elif external_power == '02':
                external_power = "Bem baixa bateria"
            elif external_power == '03':
                external_power = "Bateria baixa"
            elif external_power == '04':
                external_power = "Bateria média"
            elif external_power == '05':
                external_power = "Bateria alta"
            elif external_power == '06':
                external_power = "Bateria extremamente alta"
            else: 
                external_power = "Desconhecido"

            dados = f"{converter_para_brasil(send_time_utc)},{imei},{serial_number},{Tipo_mensagem},77,GT06V4,,,{external_power},{acc}," \
                    f"{satelites_in_use},,{speed},{course_info['azimute']},{latitude:.6f},{longitude:.6f},{mcc},{mnc},{lac},{cell_id},{course_info['realtime_gps']},{course_info['gps_posicionado']},,,,,{terminal_status},{charging_status},{normal_working},{alarm_status},{gps_status},{gas_oil_status}"


            print(f"Tipo_mensagem: {Tipo_mensagem}") 
            print(f"Serial number: {serial_number}") 
            print(f"Protocol number: {protocol_number}")
            print(f"Send time: {send_time_utc}")
            print(f"Length: {length}")
            print(f"External power: {external_power}")
            print(f"GSM signal: {gsm_signal}")
            print(f"Alarm: {alarm}")
            print(f"Serial number: {serial_number}")
            print(f"Lat/Lon: {latitude:.6f}, {longitude:.6f}")
           # print(f"Longitude: {longitude:.6f}")
            print(f"MCC: {mcc}")
            print(f"MNC: {mnc}")
            print(f"LAC: {lac}")
            print(f"Cell id: {cell_id}")
            print(f"Realtime GPS: {course_info['realtime_gps']}")
            print(f"GPS posicionado: {course_info['gps_posicionado']}")
            # print(f"Milage: {milage}")
            print(f"Terminal status: {terminal_status}")
            print(f"Charging status: {charging_status}")
            print(f"Normal working: {normal_working}")
            print(f"Alarm status: {alarm_status}")
            print(f"GPS status: {gps_status}")
            print(f"Gas oil status: {gas_oil_status}")
            print(f"\n\n")



            result = {
                'tipo': Tipo_mensagem,
                'imei': imei,
                'serial': serial_number,
                'message_type': Tipo_mensagem,
                'protocol': 'GT06',
                'latitude': latitude,
                'longitude': longitude,
                'speed': speed,
                'dados': dados
            }
           # _print_result(result)
            return result

        elif protocol_number == "15":
            Tipo_mensagem = "Ack comando"
            p = 4

            length = int(hex_data[p:p+2],16)
            p += 2

            protocol = hex_data[p:p+2]
            p += 2

            info_len = int(hex_data[p:p+2],16)
            p += 2

            sequence = hex_data[p:p+8]
            p += 8

            ascii_hex = hex_data[p:-12]

            texto = bytes.fromhex(ascii_hex).decode(
                "ascii",
                errors="ignore"
            ).rstrip("\x00")
            serial = int(hex_data[-12:-8], 16)

            print(f"Tipo_mensagem: {Tipo_mensagem}")
            print(f"Serial: {serial}")
            print()
            print(texto)
            print()

            return {
                "tipo": Tipo_mensagem,
                "serial": serial,
                "texto": texto
            }

        elif protocol_number == "12":
            Tipo_mensagem = "Localização"
            p = 4

            length = hex_data[p:p+2]
            p += 2

            protocol_number = hex_data[p:p+2]
            p += 2

            send_time = hex_data[p:p+12]
            send_time_utc = hex_to_timestamp(send_time)
            p += 12

            gps = hex_data[p:p+2]
            satellites = int(gps[1],16)
            p += 2

            latitude = int(hex_data[p:p+8],16)/1800000
            p += 8

            longitude = int(hex_data[p:p+8],16)/1800000
            p += 8

            speed = int(hex_data[p:p+2],16)
            p += 2

            course = hex_data[p:p+4]
            course_info = decode_course_info(course)

            latitude, longitude = apply_coordinate_signs(
                latitude,
                longitude,
                course_info
            )

            p += 4

            mcc = hex_data[p:p+4]
            p += 4

            mnc = hex_data[p:p+2]
            p += 2

            lac = hex_data[p:p+4]
            p += 4

            cell_id = hex_data[p:p+6]
            p += 6

            serial = int(hex_data[p:p+4],16)
            p += 4


            print(f"Tipo_mensagem: {Tipo_mensagem}") 
            print(f"Serial number: {serial}") 
            print(f"Protocol number: {protocol_number}")
            print(f"Length: {length}")
            print(f"Send time: {send_time_utc}")
            print(f"Satellites: {satellites}")
            print(f"Lat/Lon: {latitude:.6f}, {longitude:.6f}")
           # print(f"Longitude: {longitude:.6f}")
            print(f"Speed: {speed}")
            print(f"Course: {course_info['azimute']}°")
            print(f"MCC: {mcc}")
            print(f"MNC: {mnc}")
            print(f"LAC: {lac}")
            print(f"Cell id: {cell_id}")
            print(f"\n\n")
            
            dados = f"{converter_para_brasil(send_time_utc)},{imei},{serial},{Tipo_mensagem},77,GT06V4,,,," \
                    f",{satellites},,{speed},{course_info['azimute']},{latitude:.6f},{longitude:.6f},{mcc},{mnc},{lac},{cell_id},,,,"
            result = {
                'tipo': Tipo_mensagem,
                'imei': imei,
                'serial': serial,
                'message_type': Tipo_mensagem,
                'protocol': 'GT06',
                'latitude': latitude,
                'longitude': longitude,
                'speed': speed,
                'dados': dados
            }
            #_print_result(result)
            return result


        else:   
            print(f"Tipo_mensagem: Protocolo {protocol_number} não implementado")
            return None
        
    except Exception as e:
        print(f"Erro ao processar dados: {str(e)}")
        return None