package kr.ai.lineosft.projectmanagement.api.project.dto;

import jakarta.validation.constraints.Max;
import jakarta.validation.constraints.Min;
import jakarta.validation.constraints.NotBlank;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

import java.time.LocalDate;

@Getter
@Setter
@NoArgsConstructor
public class PhaseRequest {

    @NotBlank(message = "단계명은 필수 입력 항목입니다.")
    private String name;

    private String description;

    private LocalDate startDate;

    private LocalDate endDate;

    @Min(0) @Max(100)
    private Integer progress;
}
