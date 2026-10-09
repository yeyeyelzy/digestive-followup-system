package com.ruoyi.web.controller.system;

import java.util.List;
import javax.servlet.http.HttpServletResponse;

import com.ruoyi.common.annotation.Anonymous;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.PutMapping;
import org.springframework.web.bind.annotation.DeleteMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;
import com.ruoyi.common.annotation.Log;
import com.ruoyi.common.core.controller.BaseController;
import com.ruoyi.common.core.domain.AjaxResult;
import com.ruoyi.common.enums.BusinessType;
import com.ruoyi.system.domain.FollowUp;
import com.ruoyi.system.service.IFollowUpService;
import com.ruoyi.common.utils.poi.ExcelUtil;
import com.ruoyi.common.core.page.TableDataInfo;

/**
 * 随访记录管理Controller
 * 
 * @author ruoyi
 * @date 2023-07-11
 */
@RestController
@Anonymous
@RequestMapping("/system/up")
public class FollowUpController extends BaseController
{
    @Autowired
    private IFollowUpService followUpService;

    /**
     * 查询随访记录管理列表
     */
    @PreAuthorize("@ss.hasPermi('system:up:list')")
    @GetMapping("/list")
    public TableDataInfo list(FollowUp followUp)
    {
        startPage();
        List<FollowUp> list = followUpService.selectFollowUpList(followUp);
        return getDataTable(list);
    }

    /**
     * 导出随访记录管理列表
     */
    @PreAuthorize("@ss.hasPermi('system:up:export')")
    @Log(title = "随访记录管理", businessType = BusinessType.EXPORT)
    @PostMapping("/export")
    public void export(HttpServletResponse response, FollowUp followUp)
    {
        List<FollowUp> list = followUpService.selectFollowUpList(followUp);
        ExcelUtil<FollowUp> util = new ExcelUtil<FollowUp>(FollowUp.class);
        util.exportExcel(response, list, "随访记录管理数据");
    }

    /**
     * 获取随访记录管理详细信息
     */
    @PreAuthorize("@ss.hasPermi('system:up:query')")
    @GetMapping(value = "/{followUpId}")
    public AjaxResult getInfo(@PathVariable("followUpId") Long followUpId)
    {
        return success(followUpService.selectFollowUpByFollowUpId(followUpId));
    }

    /**
     * 新增随访记录管理
     */
    @PreAuthorize("@ss.hasPermi('system:up:add')")
    @Log(title = "随访记录管理", businessType = BusinessType.INSERT)
    @PostMapping
    public AjaxResult add(@RequestBody FollowUp followUp)
    {
        return toAjax(followUpService.insertFollowUp(followUp));
    }

    /**
     * 修改随访记录管理
     */
    @PreAuthorize("@ss.hasPermi('system:up:edit')")
    @Log(title = "随访记录管理", businessType = BusinessType.UPDATE)
    @PutMapping
    public AjaxResult edit(@RequestBody FollowUp followUp)
    {
        return toAjax(followUpService.updateFollowUp(followUp));
    }

    /**
     * 删除随访记录管理
     */
    @PreAuthorize("@ss.hasPermi('system:up:remove')")
    @Log(title = "随访记录管理", businessType = BusinessType.DELETE)
	@DeleteMapping("/{followUpIds}")
    public AjaxResult remove(@PathVariable Long[] followUpIds)
    {
        return toAjax(followUpService.deleteFollowUpByFollowUpIds(followUpIds));
    }
}
