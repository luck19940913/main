[app]
title = WatermarkRemover
package.name = watermarkremover
package.domain = org.example
source.dir = .
source.include_exts = py,png,jpg,jpeg
version = 0.1
requirements = python3,kivy==2.1.0,opencv-python,numpy
orientation = portrait
android.permissions = READ_EXTERNAL_STORAGE,WRITE_EXTERNAL_STORAGE
android.api = 33
android.ndk = 25b
android.sdk = 24
android.accept_sdk_license = True
android.archs = arm64-v8a, armeabi-v7a
