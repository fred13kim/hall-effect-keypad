%% ADC TEST 1
% Fred Kim 11/17/2025
% First test of the ADC on the RP2350 Pico 2 board
% Testbench: Sine wave of 500 mVpp 500 Hz 0 V offset on function generator
% sampling at roughly 1000 Hz

clear; close all; clc;

fd = fopen('data/data.txt', 'r');
dat = textscan(fd, 'RAW: 0x%x, VOLTS: %f V');
fclose(fd);

N = 50;

raw = dat{1};
volts = dat{2};

raw = raw(1:N);
volts = volts(1:N);

figure;
plot(volts);
