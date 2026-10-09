package com.ruoyi.system.mapper;

import java.util.List;
import com.ruoyi.system.domain.RecipeProcedure;

/**
 * 【请填写功能名称】Mapper接口
 * 
 * @author ruoyi
 * @date 2023-07-14
 */
public interface RecipeProcedureMapper 
{
    /**
     * 查询【请填写功能名称】
     * 
     * @param recipeId 【请填写功能名称】主键
     * @return 【请填写功能名称】
     */
    public RecipeProcedure selectRecipeProcedureByRecipeId(Long recipeId);

    /**
     * 查询【请填写功能名称】列表
     * 
     * @param recipeProcedure 【请填写功能名称】
     * @return 【请填写功能名称】集合
     */
    public List<RecipeProcedure> selectRecipeProcedureList(RecipeProcedure recipeProcedure);

    /**
     * 新增【请填写功能名称】
     * 
     * @param recipeProcedure 【请填写功能名称】
     * @return 结果
     */
    public int insertRecipeProcedure(RecipeProcedure recipeProcedure);

    /**
     * 修改【请填写功能名称】
     * 
     * @param recipeProcedure 【请填写功能名称】
     * @return 结果
     */
    public int updateRecipeProcedure(RecipeProcedure recipeProcedure);

    /**
     * 删除【请填写功能名称】
     * 
     * @param recipeId 【请填写功能名称】主键
     * @return 结果
     */
    public int deleteRecipeProcedureByRecipeId(Long recipeId);

    /**
     * 批量删除【请填写功能名称】
     * 
     * @param recipeIds 需要删除的数据主键集合
     * @return 结果
     */
    public int deleteRecipeProcedureByRecipeIds(Long[] recipeIds);
}
