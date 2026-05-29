package kr.ai.lineosft.projectmanagement.domain.project.entity;

import jakarta.persistence.*;
import kr.ai.lineosft.projectmanagement.common.entity.BaseTimeEntity;
import kr.ai.lineosft.projectmanagement.domain.member.entity.Member;
import lombok.AccessLevel;
import lombok.Builder;
import lombok.Getter;
import lombok.NoArgsConstructor;

import java.time.LocalDate;
import java.util.ArrayList;
import java.util.List;

@Entity
@Getter
@NoArgsConstructor(access = AccessLevel.PROTECTED)
@Table(name = "projects")
public class Project extends BaseTimeEntity {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false)
    private String title;

    @Column(length = 1000)
    private String description;

    @Enumerated(EnumType.STRING)
    @Column(nullable = false)
    private ProjectStatus status;

    @Enumerated(EnumType.STRING)
    @Column(nullable = false)
    private ProjectMethodology methodology;

    @Column(nullable = false)
    private Integer progress;

    private LocalDate startDate;

    private LocalDate endDate;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "creator_id", nullable = false)
    private Member creator;

    @ManyToMany(fetch = FetchType.LAZY)
    @JoinTable(
        name = "project_members",
        joinColumns = @JoinColumn(name = "project_id"),
        inverseJoinColumns = @JoinColumn(name = "member_id")
    )
    private List<Member> members = new ArrayList<>();

    @Builder
    private Project(String title, String description, ProjectStatus status, ProjectMethodology methodology, Integer progress, LocalDate startDate, LocalDate endDate, List<Member> members, Member creator) {
        this.title = title;
        this.description = description;
        this.status = status != null ? status : ProjectStatus.ACTIVE;
        this.methodology = methodology != null ? methodology : ProjectMethodology.KANBAN;
        this.progress = progress != null ? progress : 0;
        this.startDate = startDate;
        this.endDate = endDate;
        if (members != null) {
            this.members = members;
        }
        this.creator = creator;
    }

    public void update(String title, String description, ProjectStatus status, ProjectMethodology methodology, Integer progress, LocalDate startDate, LocalDate endDate, List<Member> members) {
        this.title = title;
        this.description = description;
        this.status = status != null ? status : ProjectStatus.ACTIVE;
        this.methodology = methodology != null ? methodology : ProjectMethodology.KANBAN;
        this.progress = progress != null ? progress : 0;
        this.startDate = startDate;
        this.endDate = endDate;
        this.members = members != null ? members : new ArrayList<>();
    }

    public void updateProgress(Integer progress) {
        if (progress != null && progress >= 0 && progress <= 100) {
            this.progress = progress;
        }
    }

    public void updateStatus(ProjectStatus status) {
        if (status != null) {
            this.status = status;
        }
    }
}
