#ifndef MAINWINDOW_H
#define MAINWINDOW_H

#include <QMainWindow>
#include <QTimer>

QT_BEGIN_NAMESPACE
namespace Ui { class MainWindow; }
QT_END_NAMESPACE

class MainWindow : public QMainWindow
{
    Q_OBJECT

public:
    MainWindow(QWidget *parent = nullptr);
    ~MainWindow();

private slots:
    void on_pb_connect_clicked();

    void on_pb_disconnect_clicked();

    void on_pb_servoOn_clicked();

    void on_pb_servoOff_clicked();

    void on_pb_j1_plus_clicked();

    void on_pb_j1_minus_clicked();

    void on_pb_home_clicked();

    void on_pb_z10minus_clicked();
    // Read and update the robot position
    void readRobotPos();

    void on_pb_stop_clicked();

    void on_pb_z10plus_clicked();

    void on_pb_z10plus_2_clicked();

private:
    int connected;
    Ui::MainWindow *ui;
    QTimer posTimer;
};
#endif // MAINWINDOW_H
