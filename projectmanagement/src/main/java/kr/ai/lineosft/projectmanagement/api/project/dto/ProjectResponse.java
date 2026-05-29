package kr.ai.lineosft.projectmanagement.api.project.dto;

import kr.ai.lineosft.projectmanagement.domain.project.entity.Project;
import kr.ai.lineosft.projectmanagement.domain.project.entity.ProjectMethodology;
import kr.ai.lineosft.projectmanagement.domain.project.entity.ProjectStatus;
import lombok.Getter;

import java.time.LocalDate;
import java.time.LocalDateTime;
import java.util.List;
import java.util.stream.Collectors;

@Getter
public class ProjectResponse {

    private final Long id;
    private final String title;
    private final String description;
    private final ProjectStatus status;
    private final ProjectMethodology methodology;
    private final Integer progress;
    private final LocalDate startDate;
    private final LocalDate endDate;
    private final List<MemberDto> members;
    private final MemberDto creator;
    private final LocalDateTime createdAt;

    public ProjectResponse(Project project) {
        this.id = project.getId();
        this.title = project.getTitle();
        this.description = project.getDescription();
        this.status = project.getStatus();
        this.methodology = project.getMethodology();
        this.progress = project.getProgress();
        this.startDate = project.getStartDate();
        this.endDate = project.getEndDate();
        this.members = project.getMembers().stream()
                .map(MemberDto::new)
                .collect(Collectors.toList());
        this.creator = project.getCreator() != null ? new MemberDto(project.getCreator()) : null;
        this.createdAt = project.getCreatedAt();
    }

    @Getter
    public static class MemberDto {
        private final Long id;
        private final String email;
        private final String nickname;

        public MemberDto(kr.ai.lineosft.projectmanagement.domain.member.entity.Member member) {
            this.id = member.getId();
            this.email = member.getEmail();
            this.nickname = member.getNickname();
        }
    }
}
