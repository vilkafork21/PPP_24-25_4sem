#!/usr/bin/env python3
# -*- coding: utf-8 -*-
def main():
    import os
import json
import socket
import threading
import tempfile
from pydub import AudioSegment

HOST = '0.0.0.0'  # слушать на всех сетевых интерфейсах
PORT = 5002      # вы можете изменить порт по желанию

AUDIO_DIR = 'audio_files'
JSON_METADATA_FILE = 'audio_files.json'

def generate_audio_metadata(audio_dir, json_file):
    """
    Сканирует директорию с аудио, получает метаданные (имя, формат, длительность) 
    и сохраняет результат в JSON-файл.
    """
    audio_list = []
    
    # Перебираем все файлы в директории
    for filename in os.listdir(audio_dir):
        filepath = os.path.join(audio_dir, filename)
        
        # Если это файл (а не поддиректория), пробуем считать его аудио
        if os.path.isfile(filepath):
            # Определяем расширение как формат
            file_ext = os.path.splitext(filename)[1].lower().replace('.', '')
            
            try:
                # Считываем через pydub
                audio = AudioSegment.from_file(filepath)
                duration_ms = len(audio)  # длительность в миллисекундах
                duration_sec = duration_ms / 1000.0

                audio_info = {
                    "filename": filename,
                    "format": file_ext,
                    "duration_sec": duration_sec
                }
                audio_list.append(audio_info)
            except Exception as e:
                print(f"[WARNING] Файл {filename} не удалось прочитать: {e}")
    
    # Сохраняем результат в JSON
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(audio_list, f, ensure_ascii=False, indent=2)
    return audio_list

def load_audio_metadata(json_file):
    """
    Загружает аудио-метаданные из JSON-файла.
    """
    if not os.path.exists(json_file):
        return []
    with open(json_file, 'r', encoding='utf-8') as f:
        return json.load(f)

def handle_client(conn, addr, audio_list):
    """
    Обрабатывает запросы одного клиента.
    """
    print(f"[INFO] Новое подключение: {addr}")
    
    try:
        # Считаем строку запроса (протокол упрощён, читаем один запрос за раз).
        request = conn.recv(1024).decode('utf-8').strip()
        if not request:
            print(f"[INFO] Пустой запрос от {addr}, закрываем соединение.")
            return
        
        # Для удобства разобьём по пробелам
        parts = request.split()
        
        if parts[0] == 'LIST':
            # Клиент просит список аудиофайлов
            response_data = json.dumps(audio_list)
            conn.sendall(response_data.encode('utf-8'))
        
        elif parts[0] == 'CHUNK':
            # Ожидаем: CHUNK filename start_ms end_ms
            if len(parts) < 4:
                error_msg = "[ERROR] Некорректный формат команды CHUNK. Ожидается: CHUNK <filename> <start_ms> <end_ms>"
                print(error_msg)
                conn.sendall(error_msg.encode('utf-8'))
            else:
                filename = parts[1]
                start_ms = int(parts[2])
                end_ms = int(parts[3])
                
                original_path = os.path.join(AUDIO_DIR, filename)
                
                if not os.path.exists(original_path):
                    msg = f"[ERROR] Файл {filename} не найден на сервере."
                    print(msg)
                    conn.sendall(msg.encode('utf-8'))
                else:
                    # Вырезаем кусок
                    audio = AudioSegment.from_file(original_path)
                    
                    # Ограничиваем, чтобы не выходить за границы
                    start_ms = max(0, start_ms)
                    end_ms = min(len(audio), end_ms)
                    
                    if start_ms >= end_ms:
                        msg = f"[ERROR] Некорректные границы start_ms >= end_ms."
                        print(msg)
                        conn.sendall(msg.encode('utf-8'))
                    else:
                        chunk = audio[start_ms:end_ms]
                        
                        # Пишем временный файл, который потом отправим
                        with tempfile.NamedTemporaryFile(delete=False, suffix='.' + filename.split('.')[-1]) as tmp:
                            chunk.export(tmp.name, format=filename.split('.')[-1])
                            temp_path = tmp.name
                        
                        # Теперь отправим содержимое файла клиенту
                        try:
                            with open(temp_path, 'rb') as f_chunk:
                                chunk_data = f_chunk.read()
                                conn.sendall(chunk_data)
                        finally:
                            # Удаляем временный файл
                            os.remove(temp_path)
        else:
            msg = f"[ERROR] Неизвестная команда: {request}"
            print(msg)
            conn.sendall(msg.encode('utf-8'))
    
    except Exception as e:
        print(f"[ERROR] Возникла ошибка при обработке клиента {addr}: {e}")
    finally:
        print(f"[INFO] Закрываем соединение с {addr}")
        conn.close()

def start_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # Позволяет переиспользовать порт
    server_socket.bind((HOST, PORT))
    server_socket.listen(5)
    print(f"[INFO] Сервер запущен и слушает {HOST}:{PORT}")
    audio_list = load_audio_metadata(JSON_METADATA_FILE)
    try:
        while True:
            conn, addr = server_socket.accept()
            client_thread = threading.Thread(target=handle_client, args=(conn, addr, audio_list))
            client_thread.start()
    finally:
        server_socket.close()


def main():
    # 1. Создаём или обновляем JSON со списком аудиофайлов
    print("[INFO] Генерация (или обновление) списка аудиофайлов...")
    audio_list = generate_audio_metadata(AUDIO_DIR, JSON_METADATA_FILE)
    print(f"[INFO] Найдено аудиофайлов: {len(audio_list)}")

    # 2. Запуск сервера
    start_server()

if __name__ == "__main__":
    main()

