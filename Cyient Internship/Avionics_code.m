clc;
clear all;
close all;
 
f = 1923; % signal frequency
t = 0:0.000002:(1/f)*12; % generation of the time sequence 
x = (5/0.707)*sin(2*pi*f*t);%primary of rvdt (divided by 0.707 because it is rms and we need amplitude)
previous_error=0; %error computed in the previous REU frame rate calculation
 
 
deg = input('Enter the angle required for the nosewheel: ');
if deg>85 || deg<-85
    disp('Invalid Input');%nose wheel angle can't be greater than 85 or less than -85
    disp(' ');
else
 

y1 = (5*0.75*0.0088/0.707)*deg*sin(2*pi*f*t); %secondary voltage(Va-Vb) without sampling
 
Fs= 24992; %Sampling frequency
t1 = 0:1/Fs:(1/f)*12;
y2= (0.033/0.707)*deg*sin(2*pi*f*t1);%secondary voltage (Va-Vb) with sampling rate 24992 Hz 
 
 
M=1:1923;
bf= M(randi(numel(M)));
bf1=M(randi(numel(M)));%generates a random frequency from the range 1-1923
y=y2+1.25*sin(2*pi*bf*t1)+2*cos(2*pi*bf1*t1); %to be used to generate noise which corrupts
%the signal at the secondary of the RVDT
 
N=143;
k = (f/Fs)*N;%goertzel filter implementation to find the frequency bin
e = exp(-1i*2*pi*k/N);
 
w(1)=y(1);%lines 34-39 are the goertzel filter difference equations
w(2)= 2*cos(2*pi*k/N)*w(1)+y(2);
for n=3:144
    w(n)=2*cos(2*pi*k/N)*w(n-1)-w(n-2)+y(n);
end
op1 = w(144)-e*w(143);
op = abs(op1*2/N)*0.707; %to find the magnitude, the output of the filter is multiplied by 2 to get double sided spectrum
%and divided by N for compensation, multiplied by 0.707 to give rms value
 
if angle(op1)<0
    angl(j)= round(op/0.033);
else angl(j)= -1*round(op/0.033); %divided by the ratio metric sensitivity which gives value of angle
end
 
if angl(j)>85
    angl(j)=85;
end
if angl(j)<-85
        angl(j)=-85;%to ensure rvdt angle doesn't cross the limits -85 and 85
end
 
%Now the REU Frame rate is 8ms so every 8ms a new error value would be
%observed
disp('The rvdt angle that is fed into the control loop is '), disp(angl(200));
error=deg-angl(200);%error by subtracting the rvdt angle with the reu command angle
Kp=2.5*10^-3; Kd=0.1*10^-6;T=8*10^-3; %Kp is 2.5mA/deg, Kd is 0.1 mA ms/deg and T is REU frame rate
 
while error~=0 %PD controller implementation
error=deg-angl(200); 
output=Kp*error+Kd*(error-previous_error)/T;
if output>7.6*10^-3
    crrnt=8*10^-3;
    angl(200)=angl(200)+0.08;%as the nosewheel moves 10 deg in 1sec, it will move 0.08 deg in 8ms
else if output<-7.6*10^-3
        crrnt=-8*10^-3;
        angl(200)=angl(200)-0.08;
    end
end
if output<=7.6*10^-3&&output>=-7.6*10^-3
    crrnt=output;
    cangle=angl(200)+error;
    break;%once the current has reached a safe value, linear relation is used and the loop is broken
end
previous_error=error;
 
end
 
if error==0 %due to previous_error a small value of current may still be used even if error is 0
    output=Kp*error+Kd*(error-previous_error)/T;
    crrnt=output;
    cangle=angl(200);
end
 
 
disp('The final current fed to the valve is '), disp(crrnt);
disp('The corrected angle after using the control loop is '), disp(cangle);
 
end
 
%to plot the fft of signal without noise and with noise
X = fft(y2,143); % fft(x, M) can be used to control the DFT length
l = length(X)/2;
f = (0:(l-1))*Fs/(2*l);%this is basically done to plot the single sided spectrum
figure(1),subplot(2,1,1),plot(f,abs(X(1:l)*(0.707*2/N)/0.033));zoom on;
title('Magnitude Response'), grid on;
X = fft(y,143); % fft(x, M) can be used to control the DFT length
l = length(X)/2;
f = (0:(l-1))*Fs/(2*l);
subplot(2,1,2), plot(f,abs(X(1:l)*(0.707*2/N)/0.033));zoom on;
title('Magnitude Response'), grid on;
 
%to show the different assumptions of deg/sec the nose wheel moves 
t1=0:0.008:0.104;
f1=0:0.08:1.08;
figure(2), subplot(2,2,1), plot(t1,f1), title('Time taken to move 1 degree, assuming rate 10 degrees/second'), xlabel('Time(seconds)'), ylabel('Degrees'), grid on;
 
t2=0:0.008:0.2;
f2=0:0.04:1;
subplot(2,2,2), plot(t2,f2), title('Time taken to move 1 degree, assuming rate 5 degrees/second'), xlabel('Time(seconds)'), ylabel('Degrees'), grid on;
 
t3=0:0.008:1;
f3=0:0.008:1;
subplot(2,2,3), plot(t3,f3), title('Time taken to move 1 degree, assuming rate 1 degrees/second'), xlabel('Time(seconds)'), ylabel('Degrees'), grid on;
 
t4=0:0.008:0.058;
f4=0:0.16:1.16;
subplot(2,2,4), plot(t4,f4), title('Time taken to move 1 degree, assuming rate 20 degrees/second'), xlabel('Time(seconds)'), ylabel('Degrees'), grid on;
