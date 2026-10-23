cmake_minimum_required(VERSION 3.8)
project(denizalti_egitim)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

# Bağımlılıkları Bul
find_package(ament_cmake REQUIRED)
find_package(ament_cmake_python REQUIRED)
find_package(rosidl_default_generators REQUIRED)
find_package(builtin_interfaces REQUIRED)

# 1. Özel Mesaj Üretimi
rosidl_generate_interfaces(${PROJECT_NAME}
  "msg/DerinlikVerisi.msg"
  DEPENDENCIES builtin_interfaces
)

# 2. Python Paketini Kur
ament_python_install_package(${PROJECT_NAME})

# 3. Python Betiklerini Executable Olarak Hedef Klasöre Yükle
install(
  PROGRAMS
    ${CMAKE_CURRENT_SOURCE_DIR}/denizalti_egitim/derinlik_sensoru.py
    ${CMAKE_CURRENT_SOURCE_DIR}/denizalti_egitim/derinlik_gostergesi.py
  DESTINATION lib/${PROJECT_NAME}
)

# 4. Bağımlılıkları Dışa Aktar
ament_export_dependencies(rosidl_default_runtime)

ament_package()