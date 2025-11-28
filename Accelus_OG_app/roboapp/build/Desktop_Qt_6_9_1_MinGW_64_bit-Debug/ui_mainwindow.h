/********************************************************************************
** Form generated from reading UI file 'mainwindow.ui'
**
** Created by: Qt User Interface Compiler version 6.9.1
**
** WARNING! All changes made in this file will be lost when recompiling UI file!
********************************************************************************/

#ifndef UI_MAINWINDOW_H
#define UI_MAINWINDOW_H

#include <QtCore/QVariant>
#include <QtWidgets/QApplication>
#include <QtWidgets/QMainWindow>
#include <QtWidgets/QMenuBar>
#include <QtWidgets/QPushButton>
#include <QtWidgets/QScrollBar>
#include <QtWidgets/QStatusBar>
#include <QtWidgets/QWidget>

QT_BEGIN_NAMESPACE

class Ui_MainWindow
{
public:
    QWidget *centralwidget;
    QPushButton *pb_connect;
    QPushButton *pb_disconnect;
    QPushButton *pb_servoOn;
    QPushButton *pb_servoOff;
    QPushButton *pb_j1_plus;
    QPushButton *pb_j1_minus;
    QPushButton *pb_home;
    QPushButton *pb_z10minus;
    QPushButton *pb_stop;
    QScrollBar *verticalScrollBar;
    QPushButton *pb_z10plus;
    QPushButton *pb_z10plus_2;
    QMenuBar *menubar;
    QStatusBar *statusbar;

    void setupUi(QMainWindow *MainWindow)
    {
        if (MainWindow->objectName().isEmpty())
            MainWindow->setObjectName("MainWindow");
        MainWindow->resize(800, 600);
        centralwidget = new QWidget(MainWindow);
        centralwidget->setObjectName("centralwidget");
        pb_connect = new QPushButton(centralwidget);
        pb_connect->setObjectName("pb_connect");
        pb_connect->setGeometry(QRect(50, 70, 101, 41));
        pb_disconnect = new QPushButton(centralwidget);
        pb_disconnect->setObjectName("pb_disconnect");
        pb_disconnect->setGeometry(QRect(50, 120, 101, 51));
        pb_servoOn = new QPushButton(centralwidget);
        pb_servoOn->setObjectName("pb_servoOn");
        pb_servoOn->setGeometry(QRect(200, 70, 101, 51));
        pb_servoOff = new QPushButton(centralwidget);
        pb_servoOff->setObjectName("pb_servoOff");
        pb_servoOff->setGeometry(QRect(200, 130, 101, 51));
        pb_j1_plus = new QPushButton(centralwidget);
        pb_j1_plus->setObjectName("pb_j1_plus");
        pb_j1_plus->setGeometry(QRect(340, 70, 101, 51));
        pb_j1_minus = new QPushButton(centralwidget);
        pb_j1_minus->setObjectName("pb_j1_minus");
        pb_j1_minus->setGeometry(QRect(340, 130, 111, 61));
        pb_home = new QPushButton(centralwidget);
        pb_home->setObjectName("pb_home");
        pb_home->setGeometry(QRect(450, 70, 101, 51));
        pb_z10minus = new QPushButton(centralwidget);
        pb_z10minus->setObjectName("pb_z10minus");
        pb_z10minus->setGeometry(QRect(210, 230, 101, 51));
        pb_stop = new QPushButton(centralwidget);
        pb_stop->setObjectName("pb_stop");
        pb_stop->setGeometry(QRect(210, 360, 101, 51));
        verticalScrollBar = new QScrollBar(centralwidget);
        verticalScrollBar->setObjectName("verticalScrollBar");
        verticalScrollBar->setGeometry(QRect(610, 140, 16, 160));
        verticalScrollBar->setOrientation(Qt::Vertical);
        pb_z10plus = new QPushButton(centralwidget);
        pb_z10plus->setObjectName("pb_z10plus");
        pb_z10plus->setGeometry(QRect(340, 230, 101, 51));
        pb_z10plus_2 = new QPushButton(centralwidget);
        pb_z10plus_2->setObjectName("pb_z10plus_2");
        pb_z10plus_2->setGeometry(QRect(470, 230, 101, 51));
        MainWindow->setCentralWidget(centralwidget);
        menubar = new QMenuBar(MainWindow);
        menubar->setObjectName("menubar");
        menubar->setGeometry(QRect(0, 0, 800, 21));
        MainWindow->setMenuBar(menubar);
        statusbar = new QStatusBar(MainWindow);
        statusbar->setObjectName("statusbar");
        MainWindow->setStatusBar(statusbar);

        retranslateUi(MainWindow);

        QMetaObject::connectSlotsByName(MainWindow);
    } // setupUi

    void retranslateUi(QMainWindow *MainWindow)
    {
        MainWindow->setWindowTitle(QCoreApplication::translate("MainWindow", "MainWindow", nullptr));
        pb_connect->setText(QCoreApplication::translate("MainWindow", "Connect", nullptr));
        pb_disconnect->setText(QCoreApplication::translate("MainWindow", "Disconnect", nullptr));
        pb_servoOn->setText(QCoreApplication::translate("MainWindow", "Servo On", nullptr));
        pb_servoOff->setText(QCoreApplication::translate("MainWindow", "Servo Off", nullptr));
        pb_j1_plus->setText(QCoreApplication::translate("MainWindow", "Jog J1 +10", nullptr));
        pb_j1_minus->setText(QCoreApplication::translate("MainWindow", "Jog J1 -10", nullptr));
        pb_home->setText(QCoreApplication::translate("MainWindow", "HOME", nullptr));
        pb_z10minus->setText(QCoreApplication::translate("MainWindow", "Z -100", nullptr));
        pb_stop->setText(QCoreApplication::translate("MainWindow", "Stop", nullptr));
        pb_z10plus->setText(QCoreApplication::translate("MainWindow", "Z +100", nullptr));
        pb_z10plus_2->setText(QCoreApplication::translate("MainWindow", "XYZ 100", nullptr));
    } // retranslateUi

};

namespace Ui {
    class MainWindow: public Ui_MainWindow {};
} // namespace Ui

QT_END_NAMESPACE

#endif // UI_MAINWINDOW_H
