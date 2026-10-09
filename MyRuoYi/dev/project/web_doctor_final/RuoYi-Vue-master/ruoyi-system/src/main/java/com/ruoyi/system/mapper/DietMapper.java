package com.ruoyi.system.mapper;

import java.util.List;
import com.ruoyi.system.domain.Diet;

/**
 * 饮食日记管理Mapper接口
 * 
 * @author ruoyi
 * @date 2023-07-11
 */
public interface DietMapper 
{
    /**
     * 查询饮食日记管理
     * 
     * @param dietId 饮食日记管理主键
     * @return 饮食日记管理
     */
    public Diet selectDietByDietId(Long dietId);

    /**
     * 查询饮食日记管理列表
     * 
     * @param diet 饮食日记管理
     * @return 饮食日记管理集合
     */
    public List<Diet> selectDietList(Diet diet);

    /**
     * 查询饮食日记管理列表
     *
     * @param diet 饮食日记管理
     * @return 饮食日记管理集合
     */
    public List<Diet> searchByIdDate(Diet diet);

    /**
     * 新增饮食日记管理
     * 
     * @param diet 饮食日记管理
     * @return 结果
     */
    public int insertDiet(Diet diet);

    /**
     * 修改饮食日记管理
     * 
     * @param diet 饮食日记管理
     * @return 结果
     */
    public int updateDiet(Diet diet);

    /**
     * 修改饮食日记管理
     *
     * @param diet 饮食日记管理
     * @return 结果
     */
    public int updateIdDate(Diet diet);

    /**
     * 删除饮食日记管理
     * 
     * @param dietId 饮食日记管理主键
     * @return 结果
     */
    public int deleteDietByDietId(Long dietId);

    /**
     * 批量删除饮食日记管理
     * 
     * @param dietIds 需要删除的数据主键集合
     * @return 结果
     */
    public int deleteDietByDietIds(Long[] dietIds);
}
