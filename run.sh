sudo /home/pi/miniconda3/envs/rpi-test-platform/bin/python app.py &
sleep 7s
python gpio_manager.py &
sudo /home/pi/miniconda3/envs/rpi-test-platform/bin/python ocd/ocd_wrapper.py