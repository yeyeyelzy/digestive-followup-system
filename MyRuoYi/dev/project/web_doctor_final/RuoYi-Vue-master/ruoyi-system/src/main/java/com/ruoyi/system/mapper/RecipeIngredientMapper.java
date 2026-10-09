package com.ruoyi.system.mapper;

import java.util.List;
import com.ruoyi.system.domain.RecipeIngredient;

/**
 * 【请填写功能名称】Mapper接口
 * 
 * @author ruoyi
 * @date 2023-07-14
 */
public interface RecipeIngredientMapper 
{
    /**
     * 查询【请填写功能名称】
     * 
     * @param recipeId 【请填写功能名称】主键
     * @return 【请填写功能名称】
     */
    public RecipeIngredient selectRecipeIngredientByRecipeId(Long recipeId);

    /**
     * 查询【请填写功能名称】列表
     * 
     * @param recipeIngredient 【请填写功能名称】
     * @return 【请填写功能名称】集合
     */
    public List<RecipeIngredient> selectRecipeIngredientList(RecipeIngredient recipeIngredient);

    /**
     * 新增【请填写功能名称】
     * 
     * @param recipeIngredient 【请填写功能名称】
     * @return 结果
     */
    public int insertRecipeIngredient(RecipeIngredient recipeIngredient);

    /**
     * 修改【请填写功能名称】
     * 
     * @param recipeIngredient 【请填写功能名称】
     * @return 结果
     */
    public int updateRecipeIngredient(RecipeIngredient recipeIngredient);

    /**
     * 删除【请填写功能名称】
     * 
     * @param recipeId 【请填写功能名称】主键
     * @return 结果
     */
    public int deleteRecipeIngredientByRecipeId(Long recipeId);

    /**
     * 批量删除【请填写功能名称】
     * 
     * @param recipeIds 需要删除的数据主键集合
     * @return 结果
     */
    public int deleteRecipeIngredientByRecipeIds(Long[] recipeIds);
}
