sudo /home/pi/miniconda3/envs/rpi-test-platform/bin/python app.py &
python gpio_manager.py & 
sudo /home/pi/miniconda3/envs/rpi-test-platform/bin/python python_ocd/targets/stm32l0.py
