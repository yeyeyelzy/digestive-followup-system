package com.ruoyi.system.service;

import java.util.List;
import com.ruoyi.system.domain.Living;

/**
 * 生活方式日记管理Service接口
 * 
 * @author ruoyi
 * @date 2023-07-11
 */
public interface ILivingService 
{
    /**
     * 查询生活方式日记管理
     * 
     * @param livingId 生活方式日记管理主键
     * @return 生活方式日记管理
     */
    public Living selectLivingByLivingId(Long livingId);

    /**
     * 查询生活方式日记管理列表
     * 
     * @param living 生活方式日记管理
     * @return 生活方式日记管理集合
     */
    public List<Living> selectLivingList(Living living);

    /**
     * 查询生活方式日记管理列表
     *
     * @param living 生活方式日记管理
     * @return 生活方式日记管理集合
     */
    public List<Living> searchByIdDate(Living living);

    /**
     * 新增生活方式日记管理
     * 
     * @param living 生活方式日记管理
     * @return 结果
     */
    public int insertLiving(Living living);

    /**
     * 修改生活方式日记管理
     * 
     * @param living 生活方式日记管理
     * @return 结果
     */
    public int updateLiving(Living living);

    /**
     * 修改生活方式日记管理
     *
     * @param living 生活方式日记管理
     * @return 结果
     */
    public int updateIdDate(Living living);

    /**
     * 批量删除生活方式日记管理
     * 
     * @param livingIds 需要删除的生活方式日记管理主键集合
     * @return 结果
     */
    public int deleteLivingByLivingIds(Long[] livingIds);

    /**
     * 删除生活方式日记管理信息
     * 
     * @param livingId 生活方式日记管理主键
     * @return 结果
     */
    public int deleteLivingByLivingId(Long livingId);
}
