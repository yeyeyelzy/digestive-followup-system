package com.ruoyi.system.service;

import java.util.List;
import com.ruoyi.system.domain.Files;

/**
 * 文件管理Service接口
 * 
 * @author ruoyi
 * @date 2023-07-11
 */
public interface IFilesService 
{
    /**
     * 查询文件管理
     * 
     * @param id 文件管理主键
     * @return 文件管理
     */
    public Files selectFilesById(Long id);

    /**
     * 查询文件管理列表
     * 
     * @param files 文件管理
     * @return 文件管理集合
     */
    public List<Files> selectFilesList(Files files);

    /**
     * 新增文件管理
     * 
     * @param files 文件管理
     * @return 结果
     */
    public int insertFiles(Files files);

    /**
     * 修改文件管理
     * 
     * @param files 文件管理
     * @return 结果
     */
    public int updateFiles(Files files);

    /**
     * 批量删除文件管理
     * 
     * @param ids 需要删除的文件管理主键集合
     * @return 结果
     */
    public int deleteFilesByIds(Long[] ids);

    /**
     * 删除文件管理信息
     * 
     * @param id 文件管理主键
     * @return 结果
     */
    public int deleteFilesById(Long id);
}
