sudo /home/pi/miniconda3/envs/rpi-test-platform/bin/python app.py &
sudo /home/pi/miniconda3/envs/rpi-test-platform/bin/python python_ocd/targets/stm32l0.py &
sudo /home/pi/miniconda3/envs/rpi-test-platform/bin/python module_tests/hardware_test.py &
python gpio_manager.py

