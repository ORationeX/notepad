package kr.ai.lineosft.projectmanagement.api.project.dto;

import jakarta.validation.constraints.NotBlank;
import kr.ai.lineosft.projectmanagement.domain.project.entity.SprintStatus;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

import java.time.LocalDate;

@Getter
@Setter
@NoArgsConstructor
public class SprintRequest {

    @NotBlank(message = "스프린트명은 필수 입력 항목입니다.")
    private String name;

    private String goal;

    private LocalDate startDate;

    private LocalDate endDate;

    private SprintStatus status;
}
