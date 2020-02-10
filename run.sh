sudo /home/pi/miniconda3/envs/rpi-test-platform/bin/python app.py &
sudo /home/pi/miniconda3/envs/rpi-test-platform/bin/python python_ocd/targets/stm32l0.py &
sudo /home/pi/miniconda3/envs/rpi-test-platform/bin/python module_tests/hardware_test.py &
sudo /home/pi/miniconda3/envs/rpi-test-platform/bin/python module_provision/provision.py &
sudo /home/pi/miniconda3/envs/rpi-test-platform/bin/python gpio_manager.py

