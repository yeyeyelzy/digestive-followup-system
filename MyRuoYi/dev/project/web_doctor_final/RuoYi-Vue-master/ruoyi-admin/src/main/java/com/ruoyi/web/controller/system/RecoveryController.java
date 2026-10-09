package com.ruoyi.web.controller.system;

import java.util.Date;
import java.util.HashMap;
import java.util.List;
import java.util.stream.Collectors;
import javax.servlet.http.HttpServletResponse;

import com.ruoyi.common.annotation.Anonymous;
import com.ruoyi.common.core.domain.model.LoginUser;
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
import com.ruoyi.system.domain.Recovery;
import com.ruoyi.system.service.IRecoveryService;
import com.ruoyi.common.utils.poi.ExcelUtil;
import com.ruoyi.common.core.page.TableDataInfo;

/**
 * 复查管理Controller
 * 
 * @author ruoyi
 * @date 2023-07-11
 */
@RestController
@Anonymous
@RequestMapping("/system/recovery")
public class RecoveryController extends BaseController
{
    @Autowired
    private IRecoveryService recoveryService;

    /**
     * 查询复查管理列表
     */
//    @PreAuthorize("@ss.hasPermi('system:recovery:list')")
    @GetMapping("/list")
    public TableDataInfo list(Recovery recovery)
    {
        startPage();
        List<Recovery> list = recoveryService.selectRecoveryList(recovery);
        return getDataTable(list);
    }

//    @PreAuthorize("@ss.hasPermi('system:recovery:list')")
    @GetMapping("/zhexian/{id}")
    public AjaxResult zhexian(@PathVariable String id)
    {
        Recovery recovery = new Recovery();
        List<Recovery> list = recoveryService.selectRecoveryList(recovery);
        List<Recovery> collect = list.stream().filter(e -> e.getPatientName().equals(id)).collect(Collectors.toList());


//        this.xData = response.data.data.dayList
//        this.NT_proBN = response.data.data.NtProbnpList
//        this.LVEF = response.data.data.LVEFList
//        this.峰值公斤摄氧量 = response.data.data.CPET1List
//        this.无氧公斤摄氧量 = response.data.data.CPET2List
//        this.峰值血压 = response.data.data.PeakBloodPressureList
//        this.峰值心率 = response.data.data.PpeakHeartRateList
//        this.无氧阈血压 = response.data.data.AnaerobicThresholdBloodPressureList
//        this.无氧阈心率 = response.data.data.AnaerobicThresholdHeartRateList

        List<Date> dayList = collect.stream().map(e -> e.getDate()).collect(Collectors.toList());
        List<Long> NtProbnpList = collect.stream().map(e -> e.getNtProbnp()).collect(Collectors.toList());

        List<Long> LVEFList = collect.stream().map(e -> e.getLVEF()).collect(Collectors.toList());
        List<Long> CPET1List = collect.stream().map(e -> e.getCPET1()).collect(Collectors.toList());

        List<Long> CPET2List = collect.stream().map(e -> e.getCPET2()).collect(Collectors.toList());
        List<Long> PeakBloodPressureList = collect.stream().map(e -> e.getPeakBloodPressure()).collect(Collectors.toList());

        List<Long> PpeakHeartRateList = collect.stream().map(e -> e.getPeakHeartRate()).collect(Collectors.toList());
        List<Long> AnaerobicThresholdBloodPressureList = collect.stream().map(e -> e.getPeakBloodPressure()).collect(Collectors.toList());
        List<Long> AnaerobicThresholdHeartRateList = collect.stream().map(e -> e.getAnaerobicThresholdHeartRate()).collect(Collectors.toList());

        HashMap<String, Object> map = new HashMap<>();
        map.put("dayList", dayList);
        map.put("NtProbnpList", NtProbnpList);
        map.put("LVEFList", LVEFList);
        map.put("CPET1List", CPET1List);
        map.put("CPET2List", CPET2List);
        map.put("PeakBloodPressureList", PeakBloodPressureList);
        map.put("PpeakHeartRateList", PpeakHeartRateList);
        map.put("AnaerobicThresholdBloodPressureList", AnaerobicThresholdBloodPressureList);
        map.put("AnaerobicThresholdHeartRateList", AnaerobicThresholdHeartRateList);
        return AjaxResult.success(map);


    }

    /**
     * 【患者端】查询当前登录患者的复查记录列表
     */
    @GetMapping("/my-list")
    public AjaxResult myList()
    {
        LoginUser loginUser = getLoginUser();
        if (loginUser == null || loginUser.getUserId() == null)
        {
            return AjaxResult.error("用户未登录或用户信息获取失败");
        }

        Recovery queryParam = new Recovery();
        queryParam.setPatientId(loginUser.getUserId());
        List<Recovery> list = recoveryService.selectRecoveryList(queryParam);
        return AjaxResult.success(list);
    }

    /**
     * 导出复查管理列表
     */
//    @PreAuthorize("@ss.hasPermi('system:recovery:export')")
    @Log(title = "复查管理", businessType = BusinessType.EXPORT)
    @PostMapping("/export")
    public void export(HttpServletResponse response, Recovery recovery)
    {
        List<Recovery> list = recoveryService.selectRecoveryList(recovery);
        ExcelUtil<Recovery> util = new ExcelUtil<Recovery>(Recovery.class);
        util.exportExcel(response, list, "复查管理数据");
    }

    /**
     * 获取复查管理详细信息
     */
//    @PreAuthorize("@ss.hasPermi('system:recovery:query')")
    @GetMapping(value = "/{recoveryId}")
    public AjaxResult getInfo(@PathVariable("recoveryId") Long recoveryId)
    {
        return success(recoveryService.selectRecoveryByRecoveryId(recoveryId));
    }

    /**
     * 新增复查管理
     */
//    @PreAuthorize("@ss.hasPermi('system:recovery:add')")
    @Log(title = "复查管理", businessType = BusinessType.INSERT)
    @PostMapping
    public AjaxResult add(@RequestBody Recovery recovery)
    {
        return toAjax(recoveryService.insertRecovery(recovery));
    }

    /**
     * 修改复查管理
     */
//    @PreAuthorize("@ss.hasPermi('system:recovery:edit')")
    @Log(title = "复查管理", businessType = BusinessType.UPDATE)
    @PutMapping
    public AjaxResult edit(@RequestBody Recovery recovery)
    {
        return toAjax(recoveryService.updateRecovery(recovery));
    }

    /**
     * 删除复查管理
     */
//    @PreAuthorize("@ss.hasPermi('system:recovery:remove')")
    @Log(title = "复查管理", businessType = BusinessType.DELETE)
	@DeleteMapping("/{recoveryIds}")
    public AjaxResult remove(@PathVariable Long[] recoveryIds)
    {
        return toAjax(recoveryService.deleteRecoveryByRecoveryIds(recoveryIds));
    }
}
