sudo /home/pi/miniconda3/envs/rpi-test-platform/bin/python app.py &
sleep 3s
python ocd/ocd_gpio.py &
sleep 3s
python module_detect.py