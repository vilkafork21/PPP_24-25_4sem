#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import json
import socket
import threading
import tempfile
import argparse
import time
from pydub import AudioSegment

# Настройки сервера
HOST = '0.0.0.0'       # Сервер будет слушать на всех интерфейсах
PORT = 5001            # Порт сервера; убедитесь, что он свободен
AUDIO_DIR = 'audio_files'
JSON_METADATA_FILE = 'audio_files.json'

def generate_audio_metadata(audio_dir, json_file):
    """
    Сканирует папку с аудиофайлами, извлекает метаданные (имя, длительность, формат)
    и сохраняет результат в JSON-файл.
    """
    audio_list = []
    for filename in os.listdir(audio_dir):
        # Пропускаем скрытые файлы (например, .DS_Store)
        if filename.startswith('.'):
            continue
        filepath = os.path.join(audio_dir, filename)
        if os.path.isfile(filepath):
            file_ext = os.path.splitext(filename)[1].lower().replace('.', '')
            try:
                audio = AudioSegment.from_file(filepath)
                duration_ms = len(audio)
                duration_sec = duration_ms / 1000.0
                audio_info = {
                    "name": filename,
                    "duration_sec": duration_sec,
                    "format": file_ext
                }
                audio_list.append(audio_info)
            except Exception as e:
                print(f"[WARNING] Файл {filename} не удалось прочитать: {e}")
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(audio_list, f, ensure_ascii=False, indent=4)
    return audio_list

def load_audio_metadata(json_file):
    if not os.path.exists(json_file):
        return []
    with open(json_file, 'r', encoding='utf-8') as f:
        return json.load(f)

def handle_client(conn, addr, audio_list):
    """
    Обрабатывает запросы клиента:
      - 'LIST': отправляет JSON со списком аудиофайлов.
      - 'CHUNK <filename> <start_ms> <end_ms>': вырезает заданный фрагмент аудиофайла и отправляет его клиенту.
    """
    print(f"[INFO] Новое подключение: {addr}")
    try:
        request = conn.recv(1024).decode('utf-8').strip()
        if not request:
            print(f"[INFO] Пустой запрос от {addr}, закрываем соединение.")
            return

        parts = request.split()
        command = parts[0].upper()  # Сравнение без учета регистра

        if command == 'LIST':
            response_data = json.dumps(audio_list)
            conn.sendall(response_data.encode('utf-8'))

        elif command == 'CHUNK':
            if len(parts) < 4:
                conn.sendall(
                    "[ERROR] Некорректный формат команды CHUNK. Ожидается: CHUNK <filename> <start_ms> <end_ms>"
                    .encode("utf-8")
                )
                return

            filename = parts[1]
            try:
                start_ms = int(parts[2])
                end_ms = int(parts[3])
            except ValueError:
                conn.sendall("[ERROR] start_ms и end_ms должны быть целыми числами".encode("utf-8"))
                return

            original_path = os.path.join(AUDIO_DIR, filename)
            if not os.path.exists(original_path):
                conn.sendall(f"[ERROR] Файл {filename} не найден на сервере.".encode("utf-8"))
                return

            audio = AudioSegment.from_file(original_path)
            start_ms = max(0, start_ms)
            end_ms = min(len(audio), end_ms)
            if start_ms >= end_ms:
                conn.sendall("[ERROR] Некорректные границы: start_ms >= end_ms".encode("utf-8"))
                return

            # Вырезаем аудиофрагмент
            chunk = audio[start_ms:end_ms]
            with tempfile.NamedTemporaryFile(delete=False, suffix='.' + filename.split('.')[-1]) as tmp:
                chunk.export(tmp.name, format=filename.split('.')[-1])
                temp_path = tmp.name

            try:
                with open(temp_path, 'rb') as f_chunk:
                    chunk_data = f_chunk.read()
                    conn.sendall(chunk_data)
            finally:
                os.remove(temp_path)

        else:
            conn.sendall(f"[ERROR] Неизвестная команда: {request}".encode('utf-8'))
    except Exception as e:
        print(f"[ERROR] Ошибка при обработке клиента {addr}: {e}")
    finally:
        print(f"[INFO] Закрываем соединение с {addr}")
        conn.close()

def start_server():
    """
    Запускает сервер: привязывает сокет к порту и принимает подключения.
    Каждое новое подключение обрабатывается в отдельном потоке.
    """
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
    except AttributeError:
        pass
    server_socket.bind((HOST, PORT))
    server_socket.listen(5)
    print(f"[INFO] Сервер запущен и слушает {HOST}:{PORT}")

    # Загружаем метаданные (если JSON уже существует)
    audio_list = load_audio_metadata(JSON_METADATA_FILE)
    try:
        while True:
            conn, addr = server_socket.accept()
            client_thread = threading.Thread(target=handle_client, args=(conn, addr, audio_list))
            client_thread.start()
    finally:
        server_socket.close()

def client_mode():
    """
    Клиентский режим: запрашивает у пользователя команду, подключается к серверу
    и получает ответ. Если сервер не запущен, предлагает запустить его в фоновом режиме.
    """
    SERVER_ADDRESS = ('127.0.0.1', PORT)
    user_command = input("Введите 'Список' или 'Отрезок аудиодорожки': ").strip().lower()

    if user_command == 'список':
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect(SERVER_ADDRESS)
                s.sendall(b'LIST')
                data = s.recv(8192)
                try:
                    files = json.loads(data.decode('utf-8'))
                    formatted = json.dumps(files, indent=4, ensure_ascii=False)
                    print("Аудио файлы:", formatted)
                except Exception as e:
                    print("Ошибка при парсинге ответа:", e)
        except ConnectionRefusedError as e:
            print("[ERROR] Соединение не установлено. Сервер, возможно, не запущен.")
            answer = input("Запустить сервер в этом же окне в фоновом режиме? (y/n): ").strip().lower()
            if answer == "y":
                # Запускаем сервер в отдельном потоке
                server_thread = threading.Thread(target=start_server, daemon=True)
                server_thread.start()
                print("Сервер запущен в фоновом режиме. Ждите пару секунд...")
                time.sleep(2)  # Подождать, чтобы сервер успел запуститься
                print("Попробуйте снова выполнить команду 'Список'.")
            else:
                print("Не удалось подключиться к серверу. Завершение клиента.")
        except Exception as e:
            print(f"[ERROR] Не удалось подключиться к серверу: {e}")

    elif user_command == 'отрезок аудиодорожки':
        filename = input("Введите имя аудиофайла (например, Get Lit.mp3): ").strip()
        try:
            start_ms = int(input("Введите начальное время в мс: ").strip())
            end_ms = int(input("Введите конечное время в мс: ").strip())
        except ValueError:
            print("[ERROR] Ошибка ввода: время должно быть целым числом.")
            return

        command_str = f"CHUNK {filename} {start_ms} {end_ms}"
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect(SERVER_ADDRESS)
                s.sendall(command_str.encode('utf-8'))
                chunk_data = b""
                while True:
                    packet = s.recv(4096)
                    if not packet:
                        break
                    chunk_data += packet
                out_filename = f"out_{filename}"
                with open(out_filename, "wb") as f_out:
                    f_out.write(chunk_data)
                print(f"Аудиофрагмент сохранён в файл: {out_filename}")
        except ConnectionRefusedError as e:
            print("[ERROR] Соединение не установлено. Сервер, возможно, не запущен.")
            answer = input("Запустить сервер в этом же окне в фоновом режиме? (y/n): ").strip().lower()
            if answer == "y":
                server_thread = threading.Thread(target=start_server, daemon=True)
                server_thread.start()
                print("Сервер запущен в фоновом режиме. Попробуйте снова выполнить команду.")
            else:
                print("Не удалось подключиться к серверу. Завершение клиента.")
        except Exception as e:
            print(f"[ERROR] Не удалось получить фрагмент с сервера: {e}")
    else:
        print("[ERROR] Неверная команда. Введите 'Список' или 'Отрезок аудиодорожки'.")

def main():
    parser = argparse.ArgumentParser(description="Аудио сервер / клиент")
    parser.add_argument('--mode', choices=['server', 'client'], help="Запускать сервер или клиент")
    args = parser.parse_args()
    
    if not args.mode:
        mode = input("Введите 'server' для запуска сервера или 'client' для запуска клиента: ").strip().lower()
    else:
        mode = args.mode.lower()
    
    if mode == 'server':
        print("[INFO] Генерация (или обновление) списка аудиофайлов...")
        generate_audio_metadata(AUDIO_DIR, JSON_METADATA_FILE)
        print("[INFO] Запуск сервера...")
        start_server()
    elif mode == 'client':
        print("Запуск клиента...")
        client_mode()
    else:
        print("[ERROR] Неверный режим. Используйте 'server' или 'client'.")

if __name__ == "__main__":
    main()
