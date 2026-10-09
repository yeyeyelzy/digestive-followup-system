package com.ruoyi.web.controller.system;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.io.File;
import java.nio.charset.StandardCharsets;
import java.util.List;
import javax.servlet.http.HttpServletResponse;

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
import com.ruoyi.system.domain.DoctorsAdvice;
import com.ruoyi.system.service.IDoctorsAdviceService;
import com.ruoyi.common.utils.poi.ExcelUtil;
import com.ruoyi.common.core.page.TableDataInfo;

/**
 * 医嘱管理Controller
 *
 * @author ruoyi
 * @date 2023-07-11
 */
@RestController
@RequestMapping("/system/advice")
public class DoctorsAdviceController extends BaseController
{
    @Autowired
    private IDoctorsAdviceService doctorsAdviceService;

    /**
     * MySQL utf8 (3-byte) cannot store supplementary code points (e.g. many emoji).
     * Keep CJK and normal symbols, drop unsupported code points before persistence.
     */
    private String normalizeForMysqlUtf8(String text)
    {
        if (text == null || text.isEmpty())
        {
            return "";
        }
        StringBuilder sb = new StringBuilder(text.length());
        for (int i = 0; i < text.length(); )
        {
            int cp = text.codePointAt(i);
            i += Character.charCount(cp);
            if (cp == 0x09 || cp == 0x0A || cp == 0x0D || (cp >= 0x20 && cp <= 0xFFFF))
            {
                sb.appendCodePoint(cp);
            }
        }
        return sb.toString();
    }

    private String runTextRankNotice(String notice)
    {
        String input = notice == null ? "" : notice.trim();
        if (input.isEmpty())
        {
            return input;
        }

        File script = new File("../scripts/textrank_notice.py");
        if (!script.exists())
        {
            return input;
        }

        String pythonCmd = "python";
        String pythonHome = System.getenv("PYTHON_HOME");
        if (pythonHome != null && !pythonHome.trim().isEmpty())
        {
            File pythonExe = new File(pythonHome, "python.exe");
            if (pythonExe.exists())
            {
                pythonCmd = pythonExe.getAbsolutePath();
            }
        }

        ProcessBuilder pb = new ProcessBuilder(pythonCmd, script.getAbsolutePath(), input);
        pb.environment().put("PYTHONIOENCODING", "utf-8");
        pb.environment().put("PYTHONUTF8", "1");
        pb.redirectErrorStream(true);
        StringBuilder result = new StringBuilder();

        try
        {
            Process process = pb.start();
            try (BufferedReader in = new BufferedReader(new InputStreamReader(process.getInputStream(), StandardCharsets.UTF_8)))
            {
                String line;
                while ((line = in.readLine()) != null)
                {
                    if (result.length() > 0)
                    {
                        result.append("\n");
                    }
                    result.append(line);
                }
            }
            process.waitFor();
        }
        catch (IOException | InterruptedException e)
        {
            if (e instanceof InterruptedException)
            {
                Thread.currentThread().interrupt();
            }
            return input;
        }

        String ranked = normalizeForMysqlUtf8(result.toString().trim());
        String fallback = normalizeForMysqlUtf8(input);
        return ranked.isEmpty() ? fallback : ranked;
    }

    /**
     * 【医生端】查询医嘱管理列表 (供若依后台使用)
     */
    @PreAuthorize("@ss.hasPermi('system:advice:list')")
    @GetMapping("/list")
    public TableDataInfo list(DoctorsAdvice doctorsAdvice)
    {
        startPage();
        List<DoctorsAdvice> list = doctorsAdviceService.selectDoctorsAdviceList(doctorsAdvice);
        return getDataTable(list);
    }


    /**
     * 导出医嘱管理列表
     */
    @PreAuthorize("@ss.hasPermi('system:advice:export')")
    @Log(title = "医嘱管理", businessType = BusinessType.EXPORT)
    @PostMapping("/export")
    public void export(HttpServletResponse response, DoctorsAdvice doctorsAdvice)
    {
        List<DoctorsAdvice> list = doctorsAdviceService.selectDoctorsAdviceList(doctorsAdvice);
        ExcelUtil<DoctorsAdvice> util = new ExcelUtil<DoctorsAdvice>(DoctorsAdvice.class);
        util.exportExcel(response, list, "医嘱管理数据");
    }

    /**
     * 获取医嘱管理详细信息
     */
    @PreAuthorize("@ss.hasPermi('system:advice:query')")
    @GetMapping(value = "/{doctorsAdviceId}")
    public AjaxResult getInfo(@PathVariable("doctorsAdviceId") Long doctorsAdviceId)
    {
        return success(doctorsAdviceService.selectDoctorsAdviceByDoctorsAdviceId(doctorsAdviceId));
    }

    /**
     * 新增医嘱管理
     */
    @PreAuthorize("@ss.hasPermi('system:advice:add')")
    @Log(title = "医嘱管理", businessType = BusinessType.INSERT)
    @PostMapping
    public AjaxResult add(@RequestBody DoctorsAdvice doctorsAdvice)
    {
        doctorsAdvice.setNotice(runTextRankNotice(doctorsAdvice.getNotice()));
        return toAjax(doctorsAdviceService.insertDoctorsAdvice(doctorsAdvice));
    }

    /**
     * 修改医嘱管理
     */
    @PreAuthorize("@ss.hasPermi('system:advice:edit')")
    @Log(title = "医嘱管理", businessType = BusinessType.UPDATE)
    @PutMapping
    public AjaxResult edit(@RequestBody DoctorsAdvice doctorsAdvice)
    {
        doctorsAdvice.setNotice(runTextRankNotice(doctorsAdvice.getNotice()));
        return toAjax(doctorsAdviceService.updateDoctorsAdvice(doctorsAdvice));
    }

    /**
     * 删除医嘱管理
     */
    @PreAuthorize("@ss.hasPermi('system:advice:remove')")
    @Log(title = "医嘱管理", businessType = BusinessType.DELETE)
    @DeleteMapping("/{doctorsAdviceIds}")
    public AjaxResult remove(@PathVariable Long[] doctorsAdviceIds)
    {
        return toAjax(doctorsAdviceService.deleteDoctorsAdviceByDoctorsAdviceIds(doctorsAdviceIds));
    }
}
