package kr.ai.lineosft.projectmanagement.common.dto.request;

import lombok.Getter;
import lombok.Setter;
import org.springframework.data.domain.PageRequest;
import org.springframework.data.domain.Pageable;
import org.springframework.data.domain.Sort;

@Getter
@Setter
public class PageRequestDto {
    private int page = 1;
    private int size = 10;
    private String sortBy = "id";
    private String direction = "DESC";

    @SuppressWarnings("null")
    public Pageable toPageable() {
        Sort.Direction sortDirection = Sort.Direction.fromString(direction);
        return PageRequest.of(page - 1, size, Sort.by(sortDirection, sortBy));
    }
}
