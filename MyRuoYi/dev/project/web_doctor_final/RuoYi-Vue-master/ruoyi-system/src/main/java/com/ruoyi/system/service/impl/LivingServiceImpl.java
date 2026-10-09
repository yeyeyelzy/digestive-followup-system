package com.ruoyi.system.service.impl;

import java.util.List;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import com.ruoyi.system.mapper.LivingMapper;
import com.ruoyi.system.domain.Living;
import com.ruoyi.system.service.ILivingService;

/**
 * 生活方式日记管理Service业务层处理
 * 
 * @author ruoyi
 * @date 2023-07-11
 */
@Service
public class LivingServiceImpl implements ILivingService 
{
    @Autowired
    private LivingMapper livingMapper;

    /**
     * 查询生活方式日记管理
     * 
     * @param livingId 生活方式日记管理主键
     * @return 生活方式日记管理
     */
    @Override
    public Living selectLivingByLivingId(Long livingId)
    {
        return livingMapper.selectLivingByLivingId(livingId);
    }

    /**
     * 查询生活方式日记管理列表
     * 
     * @param living 生活方式日记管理
     * @return 生活方式日记管理
     */
    @Override
    public List<Living> selectLivingList(Living living)
    {
        return livingMapper.selectLivingList(living);
    }

    /**
     * 查询生活方式日记管理列表
     *
     * @param living 生活方式日记管理
     * @return 生活方式日记管理
     */
    @Override
    public List<Living> searchByIdDate(Living living)
    {
        return livingMapper.searchByIdDate(living);
    }

    /**
     * 新增生活方式日记管理
     * 
     * @param living 生活方式日记管理
     * @return 结果
     */
    @Override
    public int insertLiving(Living living)
    {
        return livingMapper.insertLiving(living);
    }

    /**
     * 修改生活方式日记管理
     * 
     * @param living 生活方式日记管理
     * @return 结果
     */
    @Override
    public int updateLiving(Living living)
    {
        return livingMapper.updateLiving(living);
    }

    /**
     * 修改生活方式日记管理
     *
     * @param living 生活方式日记管理
     * @return 结果
     */
    @Override
    public int updateIdDate(Living living)
    {
        return livingMapper.updateIdDate(living);
    }

    /**
     * 批量删除生活方式日记管理
     * 
     * @param livingIds 需要删除的生活方式日记管理主键
     * @return 结果
     */
    @Override
    public int deleteLivingByLivingIds(Long[] livingIds)
    {
        return livingMapper.deleteLivingByLivingIds(livingIds);
    }

    /**
     * 删除生活方式日记管理信息
     * 
     * @param livingId 生活方式日记管理主键
     * @return 结果
     */
    @Override
    public int deleteLivingByLivingId(Long livingId)
    {
        return livingMapper.deleteLivingByLivingId(livingId);
    }
}
