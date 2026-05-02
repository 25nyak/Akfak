FROM budtmo/docker-android:v11.0

# Pre-install APKs
COPY telegram.apk /root/tmp/
RUN adb install /root/tmp/telegram.apk
