#include <QDebug>
#include <QDir>
#include <iostream>
#include <thread>
#include "mainwindow.h"
#include "ui_mainwindow.h"
#include "include/nrc_lib.h"


#define MY_ROBOT "robot"

MainWindow::MainWindow(QWidget *parent)
    : QMainWindow(parent)
    , ui(new Ui::MainWindow)
{
    ui->setupUi(this);

    connect(&posTimer, SIGNAL(timeout()),this, SLOT(readRobotPos()));
    posTimer.start(1000);
}

MainWindow::~MainWindow()
{
    delete ui;
}

void MainWindow::readRobotPos(){
    if (connected == 1){
        double pos[7];
        get_current_position(pos, 0, MY_ROBOT);
        qDebug() << "Joint" << pos[0] <<" " << pos[1] << " " << pos[2] << " " << pos[3] << " " << pos[4] << " " << pos[5];
        get_current_position(pos, 1, MY_ROBOT);
        qDebug() << "Cart" << pos[0] <<" " << pos[1] << " " << pos[2] << " " << pos[3] << " " << pos[4] << " " << pos[5];
        qDebug() << "RunState" << get_robot_running_state(MY_ROBOT) << " : mode " <<get_current_mode(MY_ROBOT);
    }
    return;
}


void call(int megID,std::string& message) {
    std::cout << "messageID" << megID << std::endl;
    std::cout << "message" << message << " " << message.length()<< std::endl;
}

void MainWindow::on_pb_connect_clicked()
{
    char a[100] = "192.168.3.15";
        if(0 == connect_robot(a,"6001",MY_ROBOT))
        {
            qDebug()<<"robot connect success";
            connected = 1;
        }else
        {
            qDebug()<<"connect fail";
            connected = 0;
        }
        //recv_message(call,MY_ROBOT);
}


void MainWindow::on_pb_disconnect_clicked()
{
    set_servo_state(0,MY_ROBOT);
    set_servo_poweroff(MY_ROBOT);
    qDebug() << disconnect_robot(MY_ROBOT);
    connected = 0;
}


void MainWindow::on_pb_servoOn_clicked()
{
    set_servo_state(1,MY_ROBOT);
    set_servo_poweron(MY_ROBOT);
}


void MainWindow::on_pb_servoOff_clicked()
{
     //set_current_mode(0, MY_ROBOT);
     set_servo_state(0,MY_ROBOT);
     set_servo_poweroff(MY_ROBOT);
}


void MainWindow::on_pb_j1_plus_clicked()
{
    double pos[7];
    get_current_position(pos, 0, MY_ROBOT);
    //pos[0] +=10.0;
    pos[2]+=10;
    robot_movej(pos, 30, 0, 30, 30,MY_ROBOT);
}


void MainWindow::on_pb_j1_minus_clicked()
{
    double pos[7];
    get_current_position(pos, 0, MY_ROBOT);
    pos[2] -=10.0;
    robot_movej(pos, 30, 0, 30, 30,MY_ROBOT);
}


void MainWindow::on_pb_home_clicked()
{
    double pos[7];
    for(int i=0;i<7;i++){ pos[i] = 0.0;}
    robot_movej(pos, 60, 0, 30, 30,MY_ROBOT);
}


void MainWindow::on_pb_z10minus_clicked()
{
    double pos[7];
    get_current_position(pos, 1, MY_ROBOT);
    qDebug()<<pos[0]<<" "<<pos[1]<<" "<<pos[2];
    pos[1] += 300;
    pos[2] -=300;
    robot_movel(pos,100,1,30, 30,MY_ROBOT);
}


void MainWindow::on_pb_stop_clicked()
{
    job_stop(MY_ROBOT);
}


void MainWindow::on_pb_z10plus_clicked()
{
    double pos[7];
    get_current_position(pos, 1, MY_ROBOT);
    qDebug()<<pos[0]<<" "<<pos[1]<<" "<<pos[2];
    pos[1] =50;
    robot_movel(pos,100,1,40, 40,MY_ROBOT);
}


void MainWindow::on_pb_z10plus_2_clicked()
{
    double pos[7];
    get_current_position(pos, 1, MY_ROBOT);
    qDebug()<<pos[0]<<" "<<pos[1]<<" "<<pos[2];
    //pos[0] -=300;
    pos[1] -=300;
    pos[2] -=300;
    robot_movel(pos,100,1,40, 40,MY_ROBOT);
}

