/*
 * NRC_job_operate.h
 *
 *  Created on: 2024年3月19日
 *      Author: yiixiong
 */

#ifndef INCLUDE_API_NRC_JOB_OPERATE_H_
#define INCLUDE_API_NRC_JOB_OPERATE_H_

#include "nrc_interface.h"

extern "C" {
/**
* @brief 根据文件夹上传一整个文件夹的作业文件
* @param directoryPath 目录的完整路径
*/
EXPORT_API int job_upload_by_directory(const char* directoryPath,const char* robotName);

/**
* @brief 根据文件名上传一个作业文件
* @param filePath 文件的完整路径
*/
EXPORT_API int job_upload_by_file(const char* filePath,const char* robotName);

/**
* @brief 下载所有作业文件到指定文件夹
* @param directoryPath 目录的完整路径
*/
EXPORT_API int job_download_by_directory(const char* directoryPath,bool isCover,const char* robotName);

/**
* @brief 删除指定的作业文件
* @param jobName 作业文件名
* @test 删除QQQ.JBR job_delete("QQQ","MyRobotNumber1");
*/
EXPORT_API int job_delete(const char* jobName,const char* robotName);

/**
* @brief 打开指定的作业文件
* @param jobName 作业文件名
* @test 打开QQQ.JBR job_open("QQQ","MyRobotNumber1");
*/
EXPORT_API int job_open(const char* jobName,const char* robotName);

/**
* @brief 运行指定的作业文件
* @param jobName 作业文件名
* @test 运行QQQ.JBR job_run("QQQ","MyRobotNumber1");
*/
EXPORT_API int job_run(const char* jobName,const char* robotName);

/**
* @brief 单步运行指定的作业文件的某一行
* @param jobName 作业文件名
* @param line 行号 [1,最大行号]
* @test 运行QQQ.JBR的第一行 job_step("QQQ",1,"MyRobotNumber1");
*/
EXPORT_API int job_step(const char* jobName,int line,const char* robotName);

/**
* @brief 暂停作业文件
*/
EXPORT_API int job_pause(const char* robotName);

/**
* @brief 继续运行作业文件
* @note 需要运行模式
*/
EXPORT_API int job_continue(const char* robotName);

/**
* @brief 停止作业文件
*/
EXPORT_API int job_stop(const char* robotName);

/**
* @brief 设置作业文件运行次数
* @param index 运行次数 0-无限次
*/
EXPORT_API int job_run_times(int index, const char* robotName);

/**
 * @brief 继续运行作业文件
 * @note 需要运行模式
 */
EXPORT_API int job_break_point_run(const char* robotName);

/**
 * @brief 获取当前打开的作业文件名称
 * @param jobname 当前打开的作业文件
 */
EXPORT_API int job_get_current_file(char* jobname, const char* robotName);

}

#endif /* INCLUDE_API_NRC_JOB_OPERATE_H_ */
