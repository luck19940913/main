[app]
title = WatermarkRemover
package.name = watermarkremover
package.domain = org.test
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 0.1
requirements = python3,kivy==2.2.1,opencv-python,numpy
orientation = portrait
osx.python_version = 3
osx.kivy_version = 2.2.1
fullscreen = 0
android.api = 33
android.apptheme = @android:style/Theme.Holo.Light
android.sdk = 24
android.ndk = 25b
android.archs = arm64-v8a, armeabi-v7a
android.permissions = READ_EXTERNAL_STORAGE, WRITE_EXTERNAL_STORAGE
android.use_aapt2 = True
