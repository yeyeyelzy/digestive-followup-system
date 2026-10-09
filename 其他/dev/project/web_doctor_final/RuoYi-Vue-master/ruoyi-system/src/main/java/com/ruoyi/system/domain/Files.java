package com.ruoyi.system.domain;

import org.apache.commons.lang3.builder.ToStringBuilder;
import org.apache.commons.lang3.builder.ToStringStyle;
import com.ruoyi.common.annotation.Excel;
import com.ruoyi.common.core.domain.BaseEntity;

/**
 * 文件管理对象 files
 * 
 * @author ruoyi
 * @date 2023-07-11
 */
public class Files extends BaseEntity
{
    private static final long serialVersionUID = 1L;

    /** id */
    private Long id;

    /** 文件名称 */
    @Excel(name = "文件名称")
    private String name;

    /** 文件类型 */
    @Excel(name = "文件类型")
    private String type;

    /** 文件大小(kb) */
    @Excel(name = "文件大小(kb)")
    private Long size;

    /** 下载链接 */
    @Excel(name = "下载链接")
    private String url;

    /** 文件md5 */
    @Excel(name = "文件md5")
    private String md5;

    /** 是否删除 */
    @Excel(name = "是否删除")
    private Integer isDelete;

    /** 是否禁用链接 */
    @Excel(name = "是否禁用链接")
    private Integer enable;

    public void setId(Long id) 
    {
        this.id = id;
    }

    public Long getId() 
    {
        return id;
    }
    public void setName(String name) 
    {
        this.name = name;
    }

    public String getName() 
    {
        return name;
    }
    public void setType(String type) 
    {
        this.type = type;
    }

    public String getType() 
    {
        return type;
    }
    public void setSize(Long size) 
    {
        this.size = size;
    }

    public Long getSize() 
    {
        return size;
    }
    public void setUrl(String url) 
    {
        this.url = url;
    }

    public String getUrl() 
    {
        return url;
    }
    public void setMd5(String md5) 
    {
        this.md5 = md5;
    }

    public String getMd5() 
    {
        return md5;
    }
    public void setIsDelete(Integer isDelete) 
    {
        this.isDelete = isDelete;
    }

    public Integer getIsDelete() 
    {
        return isDelete;
    }
    public void setEnable(Integer enable) 
    {
        this.enable = enable;
    }

    public Integer getEnable() 
    {
        return enable;
    }

    @Override
    public String toString() {
        return new ToStringBuilder(this,ToStringStyle.MULTI_LINE_STYLE)
            .append("id", getId())
            .append("name", getName())
            .append("type", getType())
            .append("size", getSize())
            .append("url", getUrl())
            .append("md5", getMd5())
            .append("isDelete", getIsDelete())
            .append("enable", getEnable())
            .toString();
    }
}
