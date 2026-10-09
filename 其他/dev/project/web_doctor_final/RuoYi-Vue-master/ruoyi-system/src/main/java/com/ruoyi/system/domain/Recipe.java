package com.ruoyi.system.domain;

import com.baomidou.mybatisplus.annotation.TableField;
import org.apache.commons.lang3.builder.ToStringBuilder;
import org.apache.commons.lang3.builder.ToStringStyle;
import com.ruoyi.common.annotation.Excel;
import com.ruoyi.common.core.domain.BaseEntity;

import java.util.List;

/**
 * 【请填写功能名称】对象 recipe
 * 
 * @author ruoyi
 * @date 2023-07-14
 */
public class Recipe extends BaseEntity
{
    private static final long serialVersionUID = 1L;

    /** $column.columnComment */
    @Excel(name = "${comment}", readConverterExp = "$column.readConverterExp()")
    private Long recipeId;

    /** $column.columnComment */
    @Excel(name = "${comment}", readConverterExp = "$column.readConverterExp()")
    private String recipeName;

    /** $column.columnComment */
    @Excel(name = "${comment}", readConverterExp = "$column.readConverterExp()")
    private Long authorId;

    /** $column.columnComment */
    @Excel(name = "${comment}", readConverterExp = "$column.readConverterExp()")
    private String cover;

    /** $column.columnComment */
    @Excel(name = "${comment}", readConverterExp = "$column.readConverterExp()")
    private String quote;

    /** $column.columnComment */
    @Excel(name = "${comment}", readConverterExp = "$column.readConverterExp()")
    private String flavor;

    /** $column.columnComment */
    @Excel(name = "${comment}", readConverterExp = "$column.readConverterExp()")
    private String rProcess;

    /** $column.columnComment */
    @Excel(name = "${comment}", readConverterExp = "$column.readConverterExp()")
    private String duration;

    /** $column.columnComment */
    @Excel(name = "${comment}", readConverterExp = "$column.readConverterExp()")
    private String difficulty;

    /** $column.columnComment */
    @Excel(name = "${comment}", readConverterExp = "$column.readConverterExp()")
    private String tip;

    /** $column.columnComment */
    @Excel(name = "${comment}", readConverterExp = "$column.readConverterExp()")
    private Long status;

    /** $column.columnComment */
    @Excel(name = "${comment}", readConverterExp = "$column.readConverterExp()")
    private Long likedNum;

    /** $column.columnComment */
    @Excel(name = "${comment}", readConverterExp = "$column.readConverterExp()")
    private Long collectedNum;

    /** $column.columnComment */
    @Excel(name = "${comment}", readConverterExp = "$column.readConverterExp()")
    private Long remarkNum;

    public void setRecipeId(Long recipeId) 
    {
        this.recipeId = recipeId;
    }

    public Long getRecipeId() 
    {
        return recipeId;
    }
    public void setRecipeName(String recipeName) 
    {
        this.recipeName = recipeName;
    }

    public String getRecipeName() 
    {
        return recipeName;
    }
    public void setAuthorId(Long authorId) 
    {
        this.authorId = authorId;
    }

    public Long getAuthorId() 
    {
        return authorId;
    }
    public void setCover(String cover) 
    {
        this.cover = cover;
    }

    public String getCover() 
    {
        return cover;
    }
    public void setQuote(String quote) 
    {
        this.quote = quote;
    }

    public String getQuote() 
    {
        return quote;
    }
    public void setFlavor(String flavor) 
    {
        this.flavor = flavor;
    }

    public String getFlavor() 
    {
        return flavor;
    }
    public void setrProcess(String rProcess) 
    {
        this.rProcess = rProcess;
    }

    public String getrProcess() 
    {
        return rProcess;
    }
    public void setDuration(String duration) 
    {
        this.duration = duration;
    }

    public String getDuration() 
    {
        return duration;
    }
    public void setDifficulty(String difficulty) 
    {
        this.difficulty = difficulty;
    }

    public String getDifficulty() 
    {
        return difficulty;
    }
    public void setTip(String tip) 
    {
        this.tip = tip;
    }

    public String getTip() 
    {
        return tip;
    }
    public void setStatus(Long status) 
    {
        this.status = status;
    }

    public Long getStatus() 
    {
        return status;
    }
    public void setLikedNum(Long likedNum) 
    {
        this.likedNum = likedNum;
    }

    public Long getLikedNum() 
    {
        return likedNum;
    }
    public void setCollectedNum(Long collectedNum) 
    {
        this.collectedNum = collectedNum;
    }

    public Long getCollectedNum() 
    {
        return collectedNum;
    }
    public void setRemarkNum(Long remarkNum) 
    {
        this.remarkNum = remarkNum;
    }

    public Long getRemarkNum() 
    {
        return remarkNum;
    }



    @TableField(exist = false)
    private List<RecipeIngredient> ingredients;

    @TableField(exist = false)
    private List<RecipeProcedure> procedures;
    public List<RecipeIngredient> getIngredients() {
        return ingredients;
    }

    public void setIngredients(List<RecipeIngredient> ingredients) {
        this.ingredients = ingredients;
    }

    public List<RecipeProcedure> getProcedures() {
        return procedures;
    }

    public void setProcedures(List<RecipeProcedure> procedures) {
        this.procedures = procedures;
    }
    @Override
    public String toString() {
        return new ToStringBuilder(this,ToStringStyle.MULTI_LINE_STYLE)
            .append("recipeId", getRecipeId())
            .append("recipeName", getRecipeName())
            .append("authorId", getAuthorId())
            .append("cover", getCover())
            .append("quote", getQuote())
            .append("flavor", getFlavor())
            .append("rProcess", getrProcess())
            .append("duration", getDuration())
            .append("difficulty", getDifficulty())
            .append("tip", getTip())
            .append("createTime", getCreateTime())
            .append("updateTime", getUpdateTime())
            .append("status", getStatus())
            .append("likedNum", getLikedNum())
            .append("collectedNum", getCollectedNum())
            .append("remarkNum", getRemarkNum())
            .toString();
    }
}
