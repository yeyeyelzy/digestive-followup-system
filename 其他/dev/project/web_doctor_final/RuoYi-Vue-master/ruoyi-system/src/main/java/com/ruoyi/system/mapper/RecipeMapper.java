package com.ruoyi.system.mapper;

import java.util.List;
import com.ruoyi.system.domain.Recipe;

/**
 * 【请填写功能名称】Mapper接口
 * 
 * @author ruoyi
 * @date 2023-07-14
 */
public interface RecipeMapper 
{
    /**
     * 查询【请填写功能名称】
     * 
     * @param recipeId 【请填写功能名称】主键
     * @return 【请填写功能名称】
     */
    public Recipe selectRecipeByRecipeId(Long recipeId);

    /**
     * 查询【请填写功能名称】列表
     * 
     * @param recipe 【请填写功能名称】
     * @return 【请填写功能名称】集合
     */
    public List<Recipe> selectRecipeList(Recipe recipe);

    /**
     * 新增【请填写功能名称】
     * 
     * @param recipe 【请填写功能名称】
     * @return 结果
     */
    public int insertRecipe(Recipe recipe);

    /**
     * 修改【请填写功能名称】
     * 
     * @param recipe 【请填写功能名称】
     * @return 结果
     */
    public int updateRecipe(Recipe recipe);

    /**
     * 删除【请填写功能名称】
     * 
     * @param recipeId 【请填写功能名称】主键
     * @return 结果
     */
    public int deleteRecipeByRecipeId(Long recipeId);

    /**
     * 批量删除【请填写功能名称】
     * 
     * @param recipeIds 需要删除的数据主键集合
     * @return 结果
     */
    public int deleteRecipeByRecipeIds(Long[] recipeIds);
}
