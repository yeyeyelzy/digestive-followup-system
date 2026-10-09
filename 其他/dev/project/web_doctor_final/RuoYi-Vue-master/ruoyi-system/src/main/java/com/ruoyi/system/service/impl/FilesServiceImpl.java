package com.ruoyi.system.service.impl;

import java.util.List;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import com.ruoyi.system.mapper.FilesMapper;
import com.ruoyi.system.domain.Files;
import com.ruoyi.system.service.IFilesService;

/**
 * 文件管理Service业务层处理
 * 
 * @author ruoyi
 * @date 2023-07-11
 */
@Service
public class FilesServiceImpl implements IFilesService 
{
    @Autowired
    private FilesMapper filesMapper;

    /**
     * 查询文件管理
     * 
     * @param id 文件管理主键
     * @return 文件管理
     */
    @Override
    public Files selectFilesById(Long id)
    {
        return filesMapper.selectFilesById(id);
    }

    /**
     * 查询文件管理列表
     * 
     * @param files 文件管理
     * @return 文件管理
     */
    @Override
    public List<Files> selectFilesList(Files files)
    {
        return filesMapper.selectFilesList(files);
    }

    /**
     * 新增文件管理
     * 
     * @param files 文件管理
     * @return 结果
     */
    @Override
    public int insertFiles(Files files)
    {
        return filesMapper.insertFiles(files);
    }

    /**
     * 修改文件管理
     * 
     * @param files 文件管理
     * @return 结果
     */
    @Override
    public int updateFiles(Files files)
    {
        return filesMapper.updateFiles(files);
    }

    /**
     * 批量删除文件管理
     * 
     * @param ids 需要删除的文件管理主键
     * @return 结果
     */
    @Override
    public int deleteFilesByIds(Long[] ids)
    {
        return filesMapper.deleteFilesByIds(ids);
    }

    /**
     * 删除文件管理信息
     * 
     * @param id 文件管理主键
     * @return 结果
     */
    @Override
    public int deleteFilesById(Long id)
    {
        return filesMapper.deleteFilesById(id);
    }
}
