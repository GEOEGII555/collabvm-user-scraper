@echo off

python3 main.py || (echo An error occured. && goto :EOF)
python3 make_batch_file_1.py
python3 make_batch_file_undo_1.py
python3 make_shell_script_1.py
python3 make_shell_script_undo_1.py