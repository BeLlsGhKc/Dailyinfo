# Add project specific ProGuard rules here.
# You can control the set of applied configuration files using the
# proguardFiles setting in build.gradle.kts.

# Keep Gson serialized classes
-keepattributes Signature
-keepattributes *Annotation*
-keep class com.dailyinfo.data.** { *; }
-keep class com.dailyinfo.calendar.** { *; }

# Keep Gson
-keep class com.google.gson.** { *; }
-keep class com.google.gson.reflect.TypeToken { *; }
-keep class * extends com.google.gson.reflect.TypeToken

# Keep kotlinx-datetime
-keep class kotlinx.datetime.** { *; }
